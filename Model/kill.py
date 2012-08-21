import domainobject
import player
import domainexception

class Kill(domainobject.DomainObject):
	
	_killer = None	
	_victim = None
	_verified = False
	_time = datetime.now()

	def __init__(self, id_=None):
		super(Kill, self).__init__(id_)

	def __str__(self):
		string = self._killer.getName() + " killed " + self._victim.getName() + " the kill is "
		if self._verified is False:
			string += "not "
		string += "verified"

		string += " (" + str(self._time) + ")"

		return string

	# Setters #
	def setKiller(self, killer):
		if not isinstance(killer, player.Player):
			raise domainexception.DomainException("Killer must be a Player object")

		self._killer = killer

	def setVictim(self, victim):
		if not isinstance(victim, player.Player):
			raise domainexception.DomainException("Victim must be a Player object")

		self._victim = victim

	def setVerified(self, value):
		try:
			value = bool(value)				# converts it to boolean type (1 = True and 0 = False)
		except NameError:
			raise domainexception.DomainException("You can only set verified to true or false")

		self._verified = value

	def setTime(self, time_):
		if type(time_) is "<type 'datetime.datetime'>":
			raise domainexception.DomainException("Time must a datetime object")

		self._time = time_

	# Getters #
	def getKiller(self):
		if isinstance(self._killer, int):
			from Model.Mapper.playermapper import PlayerMapper
			self._killer = PlayerMapper().find(self._killer)

		return self._killer

	def getVictim(self):
		if isinstance(self._victim, int):
			from Model.Mapper.playermapper import PlayerMapper
			self._victim = PlayerMapper().find(self._victim)

		return self._victim

	def getVerified(self):
		return self._verified

	def getTime(self):
		return self._time

	def dict(self, depth=0):
		if depth < 0:
			return { "id": self.getId() }
		else:
			return {
				"id": self.getId(),
				"verified": self.getVerified(),
				"time": str(self.getTime()),
				"victim": self.getVictim().dict(depth-1),
				"killer": self.getKiller().dict(depth-1),
			}