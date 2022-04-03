import sys
from requests import Session
from pyuseragents import random as random_useragent
from capmonster_python import RecaptchaV2Task, CapmonsterException
from json import loads
from names import get_first_name, get_last_name
from msvcrt import getch
from os import system
from urllib3 import disable_warnings
from loguru import logger
from platform import system as platform_system
from platform import platform
from multiprocessing.dummy import Pool
from dotenv import dotenv_values
from random import randint, choice


disable_warnings()
def clear(): return system('cls' if platform_system() == "Windows" else 'clear')
logger.remove()
logger.add(sys.stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")


if 'Windows' in platform():
	from ctypes import windll
	windll.kernel32.SetConsoleTitleW('MechaWorld Auto Reger | by NAZAVOD')


print('Telegram channel - https://t.me/n4z4v0d\n')


threads = int(input('Threads: '))
data_folder = str(input('Drop txt with data folder (wallet:email): '))


with open(data_folder, 'r') as file:
	data_list = file.readlines()
	wallets = [row.strip().split(':')[0] for row in data_list]
	emails = [row.strip().split(':')[-1] for row in data_list]


config = dotenv_values('env.txt')
CAPTCHA_API_KEY = str(config['CAPTCHA_API_KEY'])
capmonster = RecaptchaV2Task(CAPTCHA_API_KEY)


use_proxy = str(input('Use Proxies? (y/N): ')).lower()

if use_proxy == 'y':
	proxy_source = int(input('How take proxies? (1 - tor proxies; 2 - from file): '))

	if proxy_source == 2:
		proxy_type = str(input('Enter proxy type (http; https; socks4; socks5): '))
		proxy_folder = str(input('Drag and drop file with proxies (ip:port; user:pass@ip:port): '))


class MaxAttemps(Exception):
	def __init__(self):
		super().__init__(f'The maximum number of attempts has been exhausted')


class WrongResponse(Exception):
	def __init__(self, message):
		super().__init__(f'Wrong response, code: {str(message.status_code)}, response: {str(message.text)}')


def random_tor_proxy():
	proxy_auth = str(randint(1, 0x7fffffff)) + ':' + str(randint(1, 0x7fffffff))
	proxies = {'http': 'socks5://{}@localhost:9150'.format(proxy_auth), 'https': 'socks5://{}@localhost:9150'.format(proxy_auth)}
	return proxies


def take_random_proxy():
	with open(proxy_folder, 'r') as file:
		proxies = [row.strip() for row in file]

	return choice(proxies)


def mainth(data):

	for _ in range(3):
		try:
			session = Session()
			session.headers.update({'user-agent': random_useragent(), 'accept': '*/*', 'accept-language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7', 'referer': 'https://www.mechaworld.io/presale'})


			if use_proxy == 'y':
				if proxy_source == 1:
						session.proxies.update(random_tor_proxy())

				else:
					proxy_str = take_random_proxy()
					session.proxies.update({'http': f'{proxy_type}://{proxy_str}', 'https': f'{proxy_type}://{proxy_str}'}
					)


			r = session.get('https://www.mechaworld.io/_api/v2/dynamicmodel')

			session.headers.update({'Content-Type': 'application/json', 'Authorization': loads(r.text)['apps']['14ce1214-b278-a7e4-1373-00cebd1bef7c']['instance'], 'X-Wix-Client-Artifact-Id': 'wix-form-builder'})


			while True:
				try:
					logger.info(f'[{data[1]}] Trying to solve a captcha')
					task_id = capmonster.create_task("https://www.mechaworld.io/", "6Ld0J8IcAAAAANyrnxzrRlX1xrrdXsOmsepUYosy")
					result = capmonster.join_task_result(task_id)
					captcha_response = result.get("gRecaptchaResponse")

				except CapmonsterException as error:
					logger.error(f'[{data[1]}] Error when solving captcha: {error}')

				else:
					logger.success(f'[{data[1]}] Captcha successfully solved')

					break


			r = session.post('https://www.mechaworld.io/_api/wix-forms/v1/submit-form', json = {"formProperties":{"formName":"Whitelist Contacts","formId":"comp-kyvhx4vm"},"emailConfig":{"sendToOwnerAndEmails":{"emailIds":[]}},"viewMode":"Site","fields":[{"fieldId":"comp-kyvhx4wn4","label":"First Name","firstName":{"value":get_first_name()}},{"fieldId":"comp-kyvhx4x04","label":"Last Name","lastName":{"value":get_last_name()}},{"fieldId":"comp-kyvhx4x34","label":"Email","email":{"value":data[1],"tag":"other"}},{"fieldId":"comp-kzy7mcys","label":"Wax Wallet 2","extended":{"value":{"string":data[0]},"key":"custom.wax-id-2"}}],"labelKeys":["custom.contact"],"security":{"captcha":captcha_response}})

			if r.status_code != 200:
				raise WrongResponse(r)

		except WrongResponse as error:
			logger.error(f'[{data[1]}] {error}')

		except Exception as error:
			logger.error(f'[{data[1]}] Unexpected error: {str(error)}')

		else:
			with open('registered.txt', 'a') as file:
				file.write(f'{data[0]}:{data[1]}\n')

			logger.success(f'[{data[1]}] The work has been successfully completed')

			return True

	try:
		raise MaxAttemps()

	except MaxAttemps as error:

		with open('errors.txt', 'a') as file:
			file.write(f'{data[0]}:{data[1]}')
			
		logger.error(f'[{data[1]}] {error}')


if __name__ == '__main__':

	clear()
	pool = Pool(threads)
	result_list = pool.map(mainth, list(zip(wallets,emails)))

	logger.success('Работа успешно завершена!')
	print('\nPress Any Key To Exit..')
	getch()
	sys.exit()