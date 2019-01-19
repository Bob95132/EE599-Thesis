from abc import ABC

class Parent(ABC):
	
	def printing(self):
		print(self._words)

class Parent2(ABC):
	form = "Parent2 Setup: %s"

class Child(Parent, Parent2):
	
	def __init__(self, words):
		self._words = self.form % words
		super(Child, self).printing()
		
if __name__ == "__main__":
	Child("hello world")
