import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

import functionality


API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Assist(StatesGroup):
    method = State()


class DeleteChallenge(StatesGroup):
    challenge = State()


class AddChallenge(StatesGroup):
    challenge = State()
    source = State()


class CambridgeWord(StatesGroup):
    word = State()


class PronounceWord(StatesGroup):
    word = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        'Assist: /assist\n'
        'Get list of challenges: /get_list_of_challenges\n'
        'Choose a challenge: /choose_challenge\n'
        'Add a challenge: /add_challenge\n'
        'Delete a challenge: /delete_challenge\n'
        'Find a word on Cambridge: /cambridge_word\n'
        'Pronounce a word: /pronounce_word\n'
    )


@dp.message_handler(commands=['assist'])
async def get_method_to_assist(message: types.Message):
    await Assist.method.set()
    await message.answer('What method would you like to study? Input its name without a slash.')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    This method allows user to cancel practically any action.
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Cancelled.')


@dp.message_handler(state=Assist.method)
async def assist(message: types.Message, state: FSMContext):
    """
    This method tells in a nutshell what other methods do.
    """
    method_to_help = message.text
    async with state.proxy() as data:
        data['method'] = method_to_help
    await state.finish()
    await message.answer(f'{eval(data["method"]).__doc__}')


@dp.message_handler(commands=['get_list_of_challenges'])
async def get_list_of_challenges(message: types.Message):
    """
    This method provide each and every challenge from a Quizlet set.
    """
    list_of_challenges = '\n'.join(functionality.get_list_of_challenges())
    await message.answer(f'Here your challenges are:\n\n{list_of_challenges}')


@dp.message_handler(commands=['choose_challenge'])
async def choose_challenge(message: types.Message):
    """
    This method randomly chooses one challenge from a Quizlet set.
    """
    challenge = functionality.choose_challenge()
    await message.answer(f'I dare you to try your best at {challenge}.')


@dp.message_handler(commands=['delete_challenge'])
async def get_challenge_to_delete(message: types.Message):
    await DeleteChallenge.challenge.set()
    await message.answer('What challenge would you like to delete?')


@dp.message_handler(state=DeleteChallenge.challenge)
async def delete_challenge(message: types.Message, state: FSMContext):
    """
    This method deletes one specified challenge from a Quizlet set.
    """
    challenge_to_delete = message.text
    async with state.proxy() as data:
        data['challenge'] = challenge_to_delete
    await state.finish()
    functionality.delete_challenge(data['challenge'])


@dp.message_handler(commands=['add_challenge'])
async def get_challenge_to_add(message: types.Message):
    await AddChallenge.challenge.set()
    await message.answer('What challenge would you like to add?')


@dp.message_handler(state=AddChallenge.challenge)
async def get_source_to_add(message: types.Message, state: FSMContext):
    challenge_to_add = message.text
    async with state.proxy() as data:
        data['challenge'] = challenge_to_add
    await AddChallenge.next()
    await message.answer(
        'What source connected to your challenge would you like to add? If there is no need to add any, input an'
        'ellipsis.'
    )


@dp.message_handler(state=AddChallenge.source)
async def add_challenge(message: types.Message, state: FSMContext):
    """
    This method adds one specified challenge to a Quizlet set. The challenge should have two constituents: the former
    is its name, the latter is a link to some relative source this challenge might require. If there is not such a
    source, you have to input an ellipsis instead.
    """
    source_to_add = message.text
    async with state.proxy() as data:
        data['source'] = source_to_add
    await state.finish()
    functionality.add_challenge(data['challenge'], data['source'])


@dp.message_handler(commands=['cambridge_word'])
async def get_word_to_cambridge(message: types.Message):
    await CambridgeWord.word.set()
    await message.answer('What word would you like to seek on Cambridge?')


@dp.message_handler(state=CambridgeWord.word)
async def cambridge_word(message: types.Message, state: FSMContext):
    """
    This method opens Cambridge Essential American English dictionary
    https://dictionary.cambridge.org/dictionary/essential-american-english/ with a specified word.
    """
    word_to_cambridge = message.text
    async with state.proxy() as data:
        data['word'] = word_to_cambridge
    await state.finish()
    functionality.cambridge_word(data['word'])


@dp.message_handler(commands=['pronounce_word'])
async def get_word_to_pronounce(message: types.Message):
    await PronounceWord.word.set()
    await message.answer('What word would you like to find out how to pronounce?')


@dp.message_handler(state=PronounceWord.word)
async def pronounce_word(message: types.Message, state: FSMContext):
    """
    This method gives all manner of ways to pronounce a specified word from Cambridge Essential American English
    dictionary https://dictionary.cambridge.org/dictionary/essential-american-english/, depending upon its part of
    speech.
    """
    word_to_pronounce = message.text
    async with state.proxy() as data:
        data['word'] = word_to_pronounce
    await state.finish()
    pronunciations: list[functionality.Pronunciations, ...] = functionality.pronounce_word(data['word'])
    if pronunciations:
        for part_of_speech, audio, transcription in pronunciations:
            await message.answer_audio(
                audio=audio,
                caption=f'Part of speech: {part_of_speech}\nTranscription: {transcription}'
            )
    else:
        await message.answer('I am afraid there is not such a word there.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
