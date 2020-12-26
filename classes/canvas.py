from typing import Dict, Tuple, TypeVar, Generic

T = TypeVar('T')


class Canvas(Generic[T]):

    def __init__(self, drawables: Dict[Tuple[int, int], T]):
        self.drawables = drawables

    def getDrawables(self):
        return self.drawables

    def setDrawables(self, drawables: Dict[Tuple[int, int], T]):
        self.drawables = drawables

    def getDrawable(self, position: Tuple[int, int]):
        return self.drawables.get(position)

    def setDrawable(self, position: Tuple[int, int], drawable: T):
        self.drawables[position] = drawable

    def deleteDrawable(self, position: Tuple[int, int]):
        self.drawables.pop(position, None)

    def updatePositions(self, position: Tuple[int, int]):
        newDrawables: Dict[Tuple[int, int], T] = {}

        for oldPosition in self.drawables.keys():
            newPosition = tuple(map(sum, zip(oldPosition, position)))

            newDrawables[newPosition] = self.drawables.get(oldPosition)

        self.setDrawables(newDrawables)
