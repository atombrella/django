import warnings
from ctypes import c_uint

from django.contrib.gis.geos import prototypes as capi
from django.contrib.gis.geos.error import GEOSException
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.utils import six
from django.utils.deprecation import RemovedInDjango20Warning
from django.utils.six.moves import range


class Point(GEOSGeometry):
    _minlength = 2
    _maxlength = 3
    has_cs = True

    def __init__(self, x=None, y=None, z=None, srid=None):
        """
        The Point object may be initialized with either a tuple, or individual
        parameters.

        For Example:
        >>> p = Point((5, 23)) # 2D point, passed in as a tuple
        >>> p = Point(5, 23, 8) # 3D point, passed in with individual parameters
        """
        if x is None:
            coords = []
        elif isinstance(x, (tuple, list)):
            # Here a tuple or list was passed in under the `x` parameter.
            coords = x
        elif isinstance(x, six.integer_types + (float,)) and isinstance(y, six.integer_types + (float,)):
            # Here X, Y, and (optionally) Z were passed in individually, as parameters.
            if isinstance(z, six.integer_types + (float,)):
                coords = [x, y, z]
            else:
                coords = [x, y]
        else:
            raise TypeError('Invalid parameters given for Point initialization.')

        point = self._create_point(len(coords), coords)

        # Initializing using the address returned from the GEOS
        #  createPoint factory.
        super(Point, self).__init__(point, srid=srid)

    def _create_point(self, ndim, coords):
        """
        Create a coordinate sequence, set X, Y, [Z], and create point
        """
        if not ndim:
            return capi.create_point(None)

        if ndim < 2 or ndim > 3:
            raise TypeError('Invalid point dimension: %s' % str(ndim))

        cs = capi.create_cs(c_uint(1), c_uint(ndim))
        i = iter(coords)
        capi.cs_setx(cs, 0, next(i))
        capi.cs_sety(cs, 0, next(i))
        if ndim == 3:
            capi.cs_setz(cs, 0, next(i))

        return capi.create_point(cs)

    def _set_list(self, length, items):
        ptr = self._create_point(length, items)
        if ptr:
            capi.destroy_geom(self.ptr)
            self._ptr = ptr
            self._set_cs()
        else:
            # can this happen?
            raise GEOSException('Geometry resulting from slice deletion was invalid.')

    def _set_single(self, index, value):
        self._cs.setOrdinate(index, 0, value)

    def __iter__(self):
        """Allows iteration over coordinates of this Point."""
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        """Returns the number of dimensions for this Point (either 0, 2 or 3)."""
        if self.empty:
            return 0
        if self.hasz:
            return 3
        else:
            return 2

    def _get_single_external(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z

    _get_single_internal = _get_single_external

    @property
    def x(self):
        """Returns the X component of the Point."""
        return self._cs.getOrdinate(0, 0)

    @x.setter
    def x(self, value):
        """Sets the X component of the Point."""
        self._cs.setOrdinate(0, 0, value)

    @property
    def y(self):
        """Returns the Y component of the Point."""
        return self._cs.getOrdinate(1, 0)

    @y.setter
    def y(self, value):
        """Sets the Y component of the Point."""
        self._cs.setOrdinate(1, 0, value)

    @property
    def z(self):
        """Returns the Z component of the Point."""
        return self._cs.getOrdinate(2, 0) if self.hasz else None

    @z.setter
    def z(self, value):
        """Sets the Z component of the Point."""
        if not self.hasz:
            raise GEOSException('Cannot set Z on 2D Point.')
        self._cs.setOrdinate(2, 0, value)

    def get_x(self):
        warnings.warn(
            "`get_x()` is deprecated, use the `x` property instead.",
            RemovedInDjango20Warning, 2
        )
        return self.x

    def set_x(self, value):
        warnings.warn(
            "`set_x()` is deprecated, use the `x` property instead.",
            RemovedInDjango20Warning, 2
        )
        self.x = value

    def get_y(self):
        warnings.warn(
            "`get_y()` is deprecated, use the `y` property instead.",
            RemovedInDjango20Warning, 2
        )
        return self.y

    def set_y(self, value):
        warnings.warn(
            "`set_y()` is deprecated, use the `y` property instead.",
            RemovedInDjango20Warning, 2
        )
        self.y = value

    def get_z(self):
        warnings.warn(
            "`get_z()` is deprecated, use the `z` property instead.",
            RemovedInDjango20Warning, 2
        )
        return self.z

    def set_z(self, value):
        warnings.warn(
            "`set_z()` is deprecated, use the `z` property instead.",
            RemovedInDjango20Warning, 2
        )
        self.z = value

    # ### Tuple setting and retrieval routines. ###
    @property
    def tuple(self):
        """Returns a tuple of the point."""
        return self._cs.tuple

    @tuple.setter
    def tuple(self, tup):
        """Sets the coordinates of the point with the given tuple."""
        self._cs[0] = tup

    def get_coords(self):
        warnings.warn(
            "`get_coords()` is deprecated, use the `tuple` property instead.",
            RemovedInDjango20Warning, 2
        )
        return self.tuple

    def set_coords(self, tup):
        warnings.warn(
            "`set_coords()` is deprecated, use the `tuple` property instead.",
            RemovedInDjango20Warning, 2
        )
        self.tuple = tup

    # The tuple and coords properties
    coords = tuple
