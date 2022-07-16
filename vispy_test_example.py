import random

from vispy import scene, app


class Label(scene.visuals.Rectangle):

    def __init__(
        self,
        text,
        center,
        color=(1.0, 1.0, 1.0, 1.0),
        face_color=(.0, .0, .0, 1.0),
        parent=None
    ):
        super(Label, self).__init__(
            center=center,
            width=0.5,
            height=0.15,
            color=face_color,
            parent=parent
        )

        scene.visuals.Text(
            text=text,
            color=color,
            parent=self
        )

        self.transform = scene.transforms.MatrixTransform()
        self.transform.translate(center)


class Actor(scene.visuals.Box):

    def __init__(self, name, pos, scale=1, parent=None):
        super(Actor, self).__init__(
            width=1.0*scale,
            height=1.0*scale,
            depth=1.0*scale,
            color=(.95, .75, 0.0, 1.0)
        )
        
        self.parent = parent
        self.transform = scene.transforms.MatrixTransform()
        
        self.unfreeze()

        self.__pos = pos
        self.__labelCenter = (0, 0, 0.25)
        self.__label = Label(text=name, center=self.__labelCenter, parent=self)

        self.freeze()

        self.transform.translate(self.__pos)

    def updateLabelOrientation(self, matrixTransform, center):
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
        
        self.__label.transform.translate(self.__labelCenter)


class GameScene(scene.SceneCanvas):
    
    def __init__(self, **kwargs):
        super(GameScene, self).__init__(**kwargs)

        self.size = 800, 600
        self.unfreeze()

        self.actor = None

        self.view = self.central_widget.add_view(border_color="y", parent=self.scene)
        self.view.camera = scene.cameras.TurntableCamera(fov=0)
    
        self.terrain = scene.visuals.Plane(
            width=5, height=5,
            parent=self.view.scene,
            direction="+z"
        )

        self.view.camera.set_range()

        self.__actors = []
        self.__rotatingCamera = False

        self.freeze()

        self.events.mouse_press.connect(self.onMousePress)
        self.events.mouse_release.connect(self.onMouseRelease)
        self.events.mouse_move.connect(self.onMouseMove)

    def onMousePress(self, event):
        
        if event.button == 1 and not self.__rotatingCamera:
            self.__rotatingCamera = True

    def onMouseRelease(self, event):

        if event.button == 1 and self.__rotatingCamera:
            self.__rotatingCamera = False

    def onMouseMove(self, event):
        
        if self.__rotatingCamera:
            for actor in self.__actors:
                actor.updateLabelOrientation(self.view.camera.transform.matrix, self.view.camera.center)

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

        actor.updateLabelOrientation(self.view.camera.transform.matrix, self.view.camera.center)
        actor.parent = self.view.scene
        self.__actors.append(actor)


def main():

    gameScene = GameScene(bgcolor=(1.0, 1.0, 1.0, 1.0), show=True, keys="interactive")

    for idx in range(5):

        actor = Actor(
            name="actor_{0}".format(idx),
            pos=(random.uniform(-2, 2), random.uniform(-1, 1), 0.15),
            scale=0.1
        )

        gameScene.addActor(actor=actor)


if __name__ == "__main__":

    random.seed("vispy is life")

    main()

    app.run()
