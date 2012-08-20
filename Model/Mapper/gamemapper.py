import mapper
import Model.game
import usermapper as UM
import gametypemapper as GTM
import mappererror
import deferredcollection
import MySQLdb as mdb

class GameMapper(mapper.Mapper):

	def __init__(self):
		super(GameMapper, self).__init__()

	def targetClass(self):
		return "Game"

	def tableName(self):
		return "games"

	def _selectStmt(self):
		return "SELECT g.*, t.name as game_type_name FROM games g LEFT JOIN game_types t ON g.game_type_id = t.id WHERE g.id = %s LIMIT 1"

	def _selectAllStmt(self):
		return "SELECT g.*, t.name as game_type_name FROM games g LEFT JOIN game_types t ON g.game_type_id = t.id LIMIT %s, %s"	

	def _deleteStmt(self, obj):
		return "DELETE FROM games WHERE id = %s LIMIT 1"
		
	def _doCreateObject(self, data):
		"""Builds the game object given the draw data returned from the database query"""
		game_ = Model.game.Game(data["id"])

		# get creator User object
		UserMapper = UM.UserMapper()
		creator = UserMapper.find(data["creator"])
		game_.setCreator(creator)

		# Build the game type information
		gt_data["id"] = data["game_type_id"]
		gt_data["name"] = data["game_type_name"]
		GameTypeMapper = GMT.GameTypeMapper()
		gametype = GTM._createObject(gt_data)		# advantage is the object is added to the object watcher for future references
		game_.setGameType(gametype)

		game_.setName(data["name"])
		game_.setTime(data["time"])
		game_.setStartTime(data["start_time"])
		game_.setEndTime(data["end_time"])

		return game_

	def _doInsert(self, obj):
		# build query
		# id, name, game_type_id, creator
		query = "INSERT INTO games VALUES(NULL, %s, %s, %s, NOW(), %s, %s)"

		# convert boolean value to int bool
		params = (obj.getName(), obj.getGameType().getId(), obj.getCreator().getId(), obj.getStartTime(), obj.getEndTime())

		# run the query
		cursor = self.db.getCursor()
		rowsAffected = cursor.execute(query, params)

		# get insert id
		id_ = cursor.lastrowid
		obj.setId(id_)

		cursor.close()

		# only if rows were changed return a success response
		if rowsAffected > 0:
			return True
		else:
			return False

	def _doUpdate(self, obj):
		# build the query
		query = "UPDATE games SET name = %s, game_type_id = %s, creator = %s, start_time = %s, end_time = %s WHERE id = %s LIMIT 1"
		params = (obj.getName(), obj.getGameType().getId(), obj.getCreator().getId(), obj.getStartTime(), obj.getEndTime(), obj.getId())

		# run the query
		cursor = self.db.getCursor()
		rowsAffected = cursor.execute(query, params)
		cursor.close()

		if rowsAffected > 0:
			return True
		else:
			return False

	def findByUser(self, user, start=0, number=50):
		if start < 0:
			raise mdb.ProgrammingError("The start point must be a positive int")

		if number > 50:
			raise mdb.ProgrammingError("You cannot select more than 50 rows at one time")

		query = """SELECT g.*, gt.name as game_type_name 
					FROM games g 
					LEFT JOIN game_types gt ON g.game_type_id = gt.id 
					LEFT JOIN players p ON p.game_id = g.id 
					LEFT JOIN users u ON p.user_id = u.id 
					WHERE u.id = %s LIMIT %s, %s"""
		params = (user.getId(), start, start+number)

		return deferredcollection.DeferredCollection(self, query, params)