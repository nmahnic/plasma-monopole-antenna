"""
Locate mouse function
"""
from typing import List, Tuple


class Event:
    """
    This is an example Event class.

    Attributes:
    x[int]: x-position
    y[int]: y-position
    """
    def __init__(self, x: int, y: int):
        """
        Initializer, taking x and y as parameters.
        """
        self.x = x
        self.y = y


def in_bounds(event: Event, axes_location: List[int],
              window_height: int, flipy: bool = True) -> bool:
    """
    Determine if the mouse input is within a given bounds.

    Parameters:
    event: An event which has an x and y attribute, which represent
           the position of the event.
    axes_location: A list of exactly 6 ints where:
                    -The first two items are where the x and y axis begin
                     (in terms of pixels starting from the *bottom left corner*
                     of the canvas).
                    -The next two values give the location of the origin
                    -The last two are where the axis end.
    """
    pxi, pyi, px0, py0, pxf, pyf = axes_location
    x = event.x
    if flipy:
        y = window_height - event.y
    else:
        y = event.y
    return (x >= pxi and x <= pxf) and (y >= pyi and y <= pyf)


def locate_mouse(event: Event,
                 bounds: List[int],
                 window_height: int,
                 axes_location: List[int],
                 flipy: bool = True
                 ) -> Tuple[float, float]:
    """
    Locate the position of the mouse with respect to the
    coordinates displayed on the plot axes.
    
    event: An event which has an x and y attribute, which represent
           the position of the event.
    bounds: A list storing the xmin, xmax, ymin, and ymax boundaries of the
            plot in this order.
    window_height: The height of the canvas.
                   This can be obtained by calling
                   [ref to gui].canvas.get_tk_widget().winfo_height()
    axes_location: A list of exactly 6 ints where:
                    -The first two items are where the x and y axis begin
                     (in terms of pixels starting from the *bottom left corner*
                     of the canvas).
                    -The next two values give the location of the origin
                    -The last two are where the axis end.
    """

    xmin, xmax, ymin, ymax = bounds
    xrange = xmax - xmin
    yrange = ymax - ymin

    x_canvas = event.x
    if flipy:
        y_canvas = window_height - event.y
    else:
        y_canvas = event.y
    pxi, pyi, px0, py0, pxf, pyf = axes_location

    pxrange = pxf - pxi
    pyrange = pyf - pyi

    x_pxl_plot = x_canvas - px0
    y_pxl_plot = y_canvas - py0

    x = x_pxl_plot*(xrange/pxrange)
    y = y_pxl_plot*(yrange/pyrange)

    # Use the following to find the canvas coordinate
    # locations of where the axes intersect and where they end:
    # self.ax.grid()
    # print ("x: %d, y: %d"%(x_canvas, y_canvas))
    # print (bounds)
    # print(x, y)

    return x, y
