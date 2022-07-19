import random

from vispy import scene, app
from PIL import Image, ImageDraw, ImageFont

class Label(scene.visuals.Rectangle):

    def __init__(
        self,
        text,
        center,
        color=(1.0, 1.0, 1.0, 1.0),
        face_color=(.0, .0, .0, 1.0),
        parent=None
    ):
        fontSize = 14
        font = ImageFont.truetype("OpenSans-Regular.ttf", fontSize)
        # print(font.getbbox(text=text))
        w, h = font.getbbox(text=text)[2:]
        super(Label, self).__init__(
            center=center,
            width=w*1.3,
            height=h*1.1,
            radius=w/10,
            color=face_color,
            parent=parent
        )
        self.unfreeze()

        
        self.text = scene.visuals.Text(
            text=text,
            color=color,
            font_size=fontSize,
            method="gpu"
        )
        self.freeze()

    def setPos(self, newPos):
        self.center = newPos


class Actor(scene.visuals.Box):

    def __init__(self, name, pos, scale=1, parent=None):
        super(Actor, self).__init__(
            width=1.0*scale,
            height=1.0*scale,
            depth=1.0*scale,
            color=(.95, .75, 0.0, 1.0)
        )
                
        self.unfreeze()

        self.parent = parent
        self.transform = scene.transforms.MatrixTransform()

        self.__pos = pos
        self.__labelCenter = (0, 0, 0.5)
        self.__label = Label(text=name, center=self.__labelCenter, parent=self)

        self.freeze()

        self.transform.translate(self.__pos)
    
    def getPos(self):
        return self.__pos

    def setParent(self, parent):
        self.parent = parent.scene
        self.__label.parent = parent
        self.__label.text.parent = parent
        self.__label.order = 1
        self.__label.text.order = 2

    def updateLabelPos(self, newPos):
        newPos[-1] -= 30
        self.__label.center = newPos
        self.__label.text.pos = newPos
    '''def updateLabelOrientation(self, matrixTransform, center):
        """
        Update the label orientation attached to the actor based on the camera
        orientation and its center

        Parameters
        ----------
        matrixTransform : array-like
            4x4 array which represent the camera orientation
        
        center : list
            center of the main camera
        
        Return
        ------
        None
        """
        
        self.__label.transform.matrix = matrixTransform

        self.__labelCenter = [-center[idx] for idx in range(len(center))]
        self.__labelCenter[-1] += 0.25
        
        self.__label.transform.translate(self.__labelCenter)'''


class GameScene(scene.SceneCanvas):
    
    def __init__(self, **kwargs):
        super(GameScene, self).__init__(**kwargs)

        # self.size = 800, 600
        self.unfreeze()

        self.view = self.central_widget.add_view(border_color="b")
        self.view.camera = scene.cameras.TurntableCamera(fov=60)
        # self.view.camera.rect = 0, 0, 1, 1
        self.terrain = scene.visuals.Plane(
            width=5, height=5,
            parent=self.view.scene,
            direction="+z"
        )
        # self.terrain.set_gl_state("additive", depth_test=False, cull_face=False)
        # self.view.camera.set_range()

        self.__actors = []
        self.__rotatingCamera = False

        self.freeze()

        self.events.mouse_wheel.connect(self.onMouseWheel)
        self.events.mouse_move.connect(self.onMouseMove)
        self.events.mouse_release.connect(self.onMouseRelease)

    def onMouseWheel(self, event):
        
        tr = self.view.scene.transform
        for actor in self.__actors:
            screenCoords = tr.map(actor.getPos())
            screenCoords /= screenCoords[-1]
            actor.updateLabelPos(screenCoords[:2])

    def onMouseRelease(self, event):
        tr = self.view.scene.transform
        for actor in self.__actors:
            screenCoords = tr.map(actor.getPos())
            screenCoords /= screenCoords[-1]
            actor.updateLabelPos(screenCoords[:2])

    def onMouseMove(self, event):

        if event.button is not None:
            tr = self.view.scene.transform
            for actor in self.__actors:
                screenCoords = tr.map(actor.getPos())
                screenCoords /= screenCoords[-1]
                actor.updateLabelPos(screenCoords[:2])

    def addActor(self, actor):
        """
        Spawn an actor on the scene given the name, position and its scale on the map

        Parameters
        ----------
        name : str
            Name of the actor. Appears on the top of the character

        pos : array-like
            Contains x, y, z coords

        scale : float
            Scale of the actor
        
        Return
        ------
        None
        """
        tr = self.view.scene.transform
        screenCoords = tr.map(actor.getPos())
        screenCoords /= screenCoords[-1]
        actor.updateLabelPos(screenCoords[:2])
        actor.setParent(self.view)
        self.__actors.append(actor)


def main():

    gameScene = GameScene(bgcolor=(1.0, 1.0, 1.0, 1.0), show=True, keys="interactive")

    for idx in range(5):

        actor = Actor(
            name="actor_{0}".format(idx),
            pos=(random.uniform(-2, 2), random.uniform(-1, 1), 0.15),
            scale=0.1
        )
        actor.order = 1
        gameScene.addActor(actor=actor)


if __name__ == "__main__":

    random.seed("vispy is life")

    main()

    app.run()
