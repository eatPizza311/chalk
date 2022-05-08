import math

from dataclasses import dataclass
from typing import Any, List

import cairo

from diagrams.bounding_box import BoundingBox
from diagrams.point import Point, ORIGIN


PyCairoContext = Any


@dataclass
class Shape:
    def get_bounding_box(self) -> BoundingBox:
        pass

    def render(self, ctx: PyCairoContext) -> None:
        pass


@dataclass
class Circle(Shape):
    radius: float

    def get_bounding_box(self) -> BoundingBox:
        tl = Point(-self.radius, -self.radius)
        br = Point(+self.radius, +self.radius)
        return BoundingBox(tl, br)

    def render(self, ctx: PyCairoContext) -> None:
        ctx.arc(ORIGIN.x, ORIGIN.y, self.radius, 0, 2 * math.pi)


@dataclass
class Rectangle(Shape):
    width: float
    height: float

    def get_bounding_box(self) -> BoundingBox:
        left = ORIGIN.x - self.width / 2
        top = ORIGIN.y - self.height / 2
        tl = Point(left, top)
        br = Point(left + self.width, top + self.height)
        return BoundingBox(tl, br)

    def render(self, ctx: PyCairoContext) -> None:
        left = ORIGIN.x - self.width / 2
        top = ORIGIN.y - self.height / 2
        ctx.rectangle(left, top, self.width, self.height)


@dataclass
class Path(Shape):
    points: List[Point]

    def get_bounding_box(self) -> BoundingBox:
        box = BoundingBox.empty()
        for p in self.points:
            box = box.enclose(p)
        return box

    def render(self, ctx: PyCairoContext) -> None:
        p, *rest = self.points
        ctx.move_to(p.x, p.y)
        for p in rest:
            ctx.line_to(p.x, p.y)


@dataclass
class Text(Shape):
    text: str

    def __post_init__(self) -> None:
        surface = cairo.RecordingSurface(cairo.Content.COLOR,
                                         None)  # type: ignore
        self.ctx = cairo.Context(surface)

    def get_bounding_box(self) -> BoundingBox:
        extents = self.ctx.text_extents(self.text)
        return BoundingBox.from_limits(
            left=extents.x_bearing,
            top=extents.y_bearing,
            right=extents.x_bearing + extents.width,
            bottom=extents.y_bearing + extents.height,
        )

    def render(self, ctx: PyCairoContext) -> None:
        ctx.select_font_face("sans-serif")
        ctx.text_path(self.text)
