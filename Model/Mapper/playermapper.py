import sys

import mapper
import Model.player
import usermapper
import gamemapper

class PlayerMapper(mapper.Mapper):

	def __init__(self):
		super(PlayerMapper, self).__init__()

	def targetClass(self):
		return "Player"

	def tableName(self):
		return "players"

	def _selectStmt(self):
		return "SELECT * FROM "+self.tableName()+" WHERE id = %s LIMIT 1"

	def _selectAllStmt(self):
		return "SELECT * FROM "+self.tableName()+" LIMIT %s, %s"	

	def _deleteStmt(self, obj):
		return "DELETE FROM "+self.tableName()+" WHERE id = %s LIMIT 1"

	def _doCreateObject(self, data):
		"""Builds the kill object using the raw data provided from the database"""
		player_ = Model.player.Player(data["id"])

		GameMapper = gamemapper.GameMapper()
		game_ = GameMapper.find(data["game_id"])

		# If the game is deleted and the player is still linked, then errors can occur
		player_.setGame(game_)

		UserMapper = usermapper.UserMapper()
		user_ = UserMapper.find(data["user_id"])

		if user_ is not None:
			player_.setUser(user_)

			player_.setName(data["name"])
			player_.setPhoto(data["photo"])
			player_.setLat(data["lat"])
			player_.setLon(data["lon"])
			player_.setScore(data["score"])
			player_.setTime(data["time"])

		return player_

	def _doInsert(self, obj):
		# build query
		# id, name, photo, game_id, user_id, lat, lon, score, time
		query = "INSERT INTO "+self.tableName()+" VALUES(NULL, %s, %s, %s, %s, %s, %s, %s, %s)"

		# convert boolean value to int bool
		params = (obj.getName(), obj.getPhoto(), obj.getGame().getId(), 
				obj.getUser().getId(), obj.getLat(), obj.getLon(), obj.getScore(), obj.getTime())

		# run the query
		cursor = self.db.getCursor()
		rowsAffected = cursor.execute(query, params)

		# get insert id
		id_ = cursor.lastrowid
		obj.setId(id_)

		cursor.close()

		if rowsAffected > 0:
			return True
		else:
			return False

	def _doUpdate(self, obj):
		# build the query
		query = """UPDATE players SET 
					name = %s, photo = %s, game_id = %s, user_id = %s, lat = %s, lon = %s, score = %s, time = %s 
					WHERE id = %s LIMIT 1"""
		params = (obj.getName(), obj.getPhoto(), obj.getGame().getId(), 
				obj.getUser().getId(), obj.getLat(), obj.getLon(), obj.getScore(), obj.getTime(), obj.getId())

		# run the query
		cursor = self.db.getCursor()
		rowsAffected = cursor.execute(query, params)
		cursor.close()

		if rowsAffected > 0:
			return True
		else:
			return False

	def getPlayersInGame(self, game, start=0, number=50):
		# check func params
		if start < 0:
			raise mdb.ProgrammingError("Start point must be a postive int")

		if number > 50:
			raise mdb.ProgrammingError("Cannot select more than 50 rows at once")

		# build the query
		query = "SELECT * FROM players WHERE game_id = %s LIMIT %s, %s"
		params = (game.getId(), start, number)

		return deferredcollection.DeferredCollection(self, query, params)