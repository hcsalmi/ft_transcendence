import json
import time
import random
import asyncio
from queue import Queue
from .models import AiMatch
from channels.db import database_sync_to_async
from matchmaker.update import update_players, update_ball
from channels.generic.websocket import AsyncWebsocketConsumer
from matchmaker.constants import PADDLE_HEIGHT, COURT_HEIGHT, COURT_WIDTH, BALL_SPEED_COF, PADDLE_SPEED_COF

class aiMatchConsumer(AsyncWebsocketConsumer):

	#### INITIATE MATCH FUNCTIONS ####
	async def init_match(self, ballSpeed, paddleSpeed):
		self.courtHeight = COURT_HEIGHT
		self.courtWidth = COURT_WIDTH
		self.paddleHeight = PADDLE_HEIGHT

		self.ballSpeed = float(ballSpeed) * BALL_SPEED_COF
		self.paddleSpeed = float(paddleSpeed) * PADDLE_SPEED_COF

		self.ball_y = COURT_HEIGHT / 2
		self.ball_x = COURT_WIDTH / 2
		self.ballDeltaY = 0.0
		self.ballDeltaX = self.ballSpeed
		self.ballHeading = 1

		self.player1Paddle_y_top = (COURT_HEIGHT - self.paddleHeight) / 2
		self.player1Paddle_x = 0.0

		self.player2Paddle_y_top = self.player1Paddle_y_top
		self.player2Paddle_x = COURT_WIDTH

		self.goalsPlayer1 = 0
		self.goalsPlayer2 = 0

		self.player1_update_queue = Queue()
		self.player2_update_queue = Queue()

	async def send_start_match(self):
		await self.send(json.dumps({
			'identity': 'start_match',
			'paddleSpeed': self.paddleSpeed,
			'paddleHeight': self.paddleHeight,
			'courtHeight': self.courtHeight,
			'courtWidth': self.courtWidth,
			'player1Paddle_y_top': self.player1Paddle_y_top,
			'player2Paddle_y_top': self.player2Paddle_y_top,
			'player1Paddle_x': self.player1Paddle_x,
			'player2Paddle_x': self.player2Paddle_x,
			'ball_y': self.ball_y,
			'ball_x': self.ball_x,
			'ballDeltaY' : self.ballDeltaY,
			'ballDeltaX' : self.ballDeltaX,
			"ballSpeed": self.ballSpeed,
			'goalsPlayer1': self.goalsPlayer1,
			'goalsPlayer2': self.goalsPlayer2,
			'player1_username': self.player1,
			'player2_username': self.player2
		}))

	async def wait_for_confirmed(self):
		start_time = time.time()

		while (self.confirmed == False):
			await self.send_start_match()
			await asyncio.sleep(2)
			if (time.time() - start_time > 15):
				await self.send(json.dumps({
					'identity': 'error',
					'message': 'Match not confirmed'
				}))
				await self.close()
				return

	############ GAME LOGIC ############

	async def predictAiCollisionPoint(self):
		try:
			timeUntilCollision = (self.player2Paddle_x - self.ball_x) / self.ballDeltaX
			predictedCollisionPoint = self.ball_y + self.ballDeltaY * timeUntilCollision
			if (predictedCollisionPoint < 0):
				predictedCollisionPoint = -predictedCollisionPoint
			elif (predictedCollisionPoint > self.courtHeight):
				predictedCollisionPoint = 2 * self.courtHeight - predictedCollisionPoint

			scoreDifference = self.goalsPlayer2 - self.goalsPlayer1
			if (scoreDifference >= 0):
				offset = random.uniform(-0.055, 0.055)
				predictedCollisionPoint += offset
				if (random.random() < 0.5 + (scoreDifference * 0.05)):
					offset = random.uniform(-0.01, 0.01)
					predictedCollisionPoint += offset

			return predictedCollisionPoint
		except:
			print("Error in Ai prediction")

	async def updateAiPaddle(self):
		await self.wait_for_confirmed()
		while True:
			try:
				if (self.ballHeading == 1):
					targetY = await self.predictAiCollisionPoint()
					if (targetY < (self.player2Paddle_y_top + self.paddleHeight / 2)):
						while (targetY < (self.player2Paddle_y_top + self.paddleHeight / 2) and (self.player2Paddle_y_top > 0)):
							self.player2_update_queue.put(self.player2Paddle_y_top - self.paddleSpeed / 10)
							await asyncio.sleep(0.01)
					elif (targetY > (self.player2Paddle_y_top + self.paddleHeight / 2)):
						while (targetY > (self.player2Paddle_y_top + self.paddleHeight / 2) and (self.player2Paddle_y_top + self.paddleHeight < 1)):
							self.player2_update_queue.put(self.player2Paddle_y_top + self.paddleSpeed / 10)
							await asyncio.sleep(0.01)
				elif (self.ballHeading == -1):
					while (0.5 < (self.player2Paddle_y_top + self.paddleHeight / 2) and (self.player2Paddle_y_top > 0)):
						self.player2_update_queue.put(self.player2Paddle_y_top - self.paddleSpeed / 10)
						await asyncio.sleep(0.01)
					while (0.5 > (self.player2Paddle_y_top + self.paddleHeight / 2) and (self.player2Paddle_y_top + self.paddleHeight < 1)):
						self.player2_update_queue.put(self.player2Paddle_y_top + self.paddleSpeed / 10)
						await asyncio.sleep(0.01)
				await asyncio.sleep(1)
			except:
				print("Error in AI")

	async def pong(self):
		await self.wait_for_confirmed()
		while (self.goalsPlayer1 < 5 and self.goalsPlayer2 < 5):
			await update_players(self)
			await update_ball(self)
			positions = {
				"ball_y": self.ball_y,
				"ball_x": self.ball_x,
				"ballDeltaY" : self.ballDeltaY,
				"ballDeltaX" : self.ballDeltaX,
				"player1Paddle_y_top": self.player1Paddle_y_top,
				"player2Paddle_y_top": self.player2Paddle_y_top,
				"goalsPlayer1": self.goalsPlayer1,
				"goalsPlayer2": self.goalsPlayer2
			}
			await self.send(json.dumps({
				'identity': 'game_update',
				'positions': positions
			}))
			await asyncio.sleep(0.01)
		if (self.goalsPlayer1 >= 5 or self.goalsPlayer2 >= 5):
			await self.send(json.dumps({
				'identity': 'game_over',
				'winner': self.player1 if self.goalsPlayer1 >= 5 else self.player2
			}))
			if self.loopTaskActive:
				self.loopTaskActive = False
				self.game_loop_task.cancel()
				self.ai_loop_task.cancel()
			try:
				await database_sync_to_async(AiMatch.objects.get)(roomId=self.room_name).delete()
			except:
				print("Match object not found")
			self.close()

	################### CONNECT AND DISCONNECT WEBSOCKETS ##################
	async def connect(self):
		try:
			self.room_name = self.scope['url_route']['kwargs']['game_room']
			matchObject = await database_sync_to_async(AiMatch.objects.get)(roomId=self.room_name)
			self.player1 = matchObject.player1
			self.player2 = matchObject.player2
			self.loopTaskActive = False
			self.confirmed = False
			await self.accept()
			await self.send(json.dumps({
				'identity': 'room_data',
				'player1': matchObject.player1,
				'player2': matchObject.player2
			}))
		except:
			print("Match object not found")
			return


	async def disconnect(self, close_code):
		try:
			await database_sync_to_async(AiMatch.objects.get)(roomId=self.room_name).delete()
			if (self.loopTaskActive):
				self.loopTaskActive = False
				self.game_loop_task.cancel()
				self.ai_loop_task.cancel()
		except:
			if (self.loopTaskActive):
				self.loopTaskActive = False
				self.game_loop_task.cancel()
				self.ai_loop_task.cancel()
		self.close()

	################### RECEIVE DATA ON WEBSOCKETS ##################
	async def receive(self, text_data):
		data = json.loads(text_data)
		if ('type' in data):
			if (data['type'] == 'received_start_match'):
				self.confirmed = True
			elif (self.loopTaskActive):
				if (data['type'] == 'paddle_position' and 'value' in data):
					self.player1_update_queue.put(data['value'])
			elif (data['type'] == 'start_match' and 'ballSpeed' in data and 'paddleSpeed' in data and not self.loopTaskActive):
				if (type(data['ballSpeed']) != float or type(data['paddleSpeed']) != float):
					await self.send(json.dumps({
						'identity': 'error',
						'message': 'Invalid data format. Data must be floats. Allowed values are ballSpeed: 0.001-0.05, paddleSpeed: 0.001-0.05'
					}))
				elif (data['ballSpeed'] < 0.001 or data['paddleSpeed'] < 0.001):
					await self.send(json.dumps({
						'identity': 'error',
						'message': 'Invalid data format. Negative values not allowed. Allowed values are ballSpeed: 0.001-0.05, paddleSpeed: 0.001-0.05'
					}))
				elif (data['ballSpeed'] > 0.05 or data['paddleSpeed'] > 0.05):
					await self.send(json.dumps({
						'identity': 'error',
						'message': 'Invalid data format. Value too high. Allowed values are ballSpeed: 0.001-0.05, paddleSpeed: 0.001-0.05'
					}))
				else:
					print("Match initiated")
					ballSpeed = data['ballSpeed']
					paddleSpeed = data['paddleSpeed']
					await self.init_match(ballSpeed, paddleSpeed)
					self.loopTaskActive = True
					self.ai_loop_task = asyncio.create_task(self.updateAiPaddle())
					self.game_loop_task = asyncio.create_task(self.pong())
		else:
			await self.send(json.dumps({
				'identity': 'error',
				'message': 'Invalid data format'
			}))
