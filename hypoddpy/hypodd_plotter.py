#!/usr/bin/env python3
"""
Creates some plots of the relocated event Catalog.

Colors (defined using ColorConverter and get_cmap) distinguish clusters.
    grey: non-relocated
    red: relocated with cluster id 1
    green: relocated with cluster id 2
    blue: relocated with cluster id 3
    yellow: relocated with cluster id 4
    orange: relocated with cluster id 5
    cyan: relocated with cluster id 6
    magenta: relocated with cluster id 7
    brown: relocated with cluster id 8
    lime: relocated with cluster id >8 or undetermined cluster_id
"""
import cartopy.crs as ccrs
import matplotlib.pylab as plt
from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter
from obspy.core.event import read_events

from .plotting.shape_selection import Polygon, Circle
from .plotting.map_cross_section import MapCrossSection


class Positions():
    """
    Simple class for EQ Positions
    """
    def __init__(self):
        """
        Set up parameters
        """
        self.latitudes = []
        self.longitudes = []
        self.depths = []

    def validate(self):
        """Returns true if all lists are same length"""
        return (len(self.latitudes) == len(self.longitudes)
                and len(self.latitudes) == len(self.depths))


class HypoDDPlotter():
    """
    Plot original and relocated events from HypoDDpy
    """

    def __init__(self, cat, map_extent=None, depth_extent=None,
                 coastlines=None, replace_scatter_with_plot=False,
                 quiet=False):
        """
        Set up parameters

        :param cat: obspy catalog.  Original events should be in origins[0],
            relocated events in origins[-1]
        :param map_extent: limits of map to plot [W, E, S, N].  If None, uses
            limits of event lon,lats plus a small buffer
        :param depth_extent: depth limits to plot [mindepth, maxdepth].  If
            None, uses limits of event depths, plus a small buffer
        :param coastlines: The name of a NaturalEarth ('10m', '50m', '110m')
            or GSHSS ('crude', 'low', 'intermediate', 'high', 'full') coastlines
            dataset to use.
        :param replace_scatter_with_plot: Use matplotlib.pyplot.plot() instead
            of matplotlib.pyplot.scatter() (temporary fix to avoid cartopy
            0.18 bug that should be fixed in cartopy 0.18.1)
        :param quiet: Do not use print statements
        """
        self.cat = cat
        self.map_extent = map_extent
        self.depth_extent = depth_extent
        self.coastlines = None
        self.file_base = 'hypoDDpy'
        self.original_filename = ""
        self.relocated_filename = ""
        self.replace_scatter_with_plot=replace_scatter_with_plot
        self.quiet = quiet

    def plot_events(self, file_base='hypoDDpy', circle=None, polygon=None,
                    coastlines=None):
        """
        Plot original and relocated events
        :param file_base: start of output filename
        :param polygon: list of [lon, lat]s defining a polygon to highlight
        :param circle: [lon, lat, radius_km] of a circle to highlight (will
            be ignored if polygon defined)
        :param coastlines: as in constructor
        """
        if coastlines:
            self.coastlines = coastlines
        if file_base:
            self.file_base = file_base
        shape=None
        if circle:
            shape=Circle(circle)
        if polygon:
            shape=Polygon(polygon)
        self._plot_original_relocated(shape=shape)
        return self.original_filename, self.relocated_filename

    def _plot_original_relocated(self, shape=None, marker_size=1):
        """
        Plot original and relocated events

        :param shape: a shape to plot and highlight events within
        :param marker_size:
        """
        self.original_filename = f"{self.file_base}_original.pdf"
        self.relocated_filename = f"{self.file_base}_relocated.pdf"

        original_pos, relocated_pos = self._extract_positions()
        self._set_plot_params(shape)
        self.marker_size = marker_size

        # Plot the original event locations.
        map_extent, depth_extent = self._plot_events(
            original_pos,
            shape=shape,
            map_extent=self.map_extent,
            depth_extent=self.depth_extent)
        plt.savefig(self.original_filename)
        if not self.quiet:
            print("Output figure: %s" % self.original_filename)

        # Plot the relocated event locations with same extents as original
        self._plot_events(
            relocated_pos,
            shape=shape,
            map_extent=map_extent,
            depth_extent=depth_extent)
        plt.savefig(self.relocated_filename)
        if not self.quiet:
            print("Output figure: %s" % self.relocated_filename)

    def _extract_positions(self):
        """
        Extract original and relocated Positions for each event
        """
        original_pos = Positions()
        relocated_pos = Positions()

        for event in self.cat:
            # The first origin is always the original
            original_pos.latitudes.append(event.origins[0].latitude)
            original_pos.longitudes.append(event.origins[0].longitude)
            original_pos.depths.append(event.origins[0].depth / 1000.0)
            
            # The last origin could  be a relocated one or an original one.
            relocated_pos.latitudes.append(event.origins[-1].latitude)
            relocated_pos.longitudes.append(event.origins[-1].longitude)
            relocated_pos.depths.append(event.origins[-1].depth / 1000.0)
        return original_pos, relocated_pos
                    
    def _set_plot_params(self, shape):
        """
        Set plot parameters for each event
        """
        color_invalid = ColorConverter().to_rgba("grey")
        cmap = get_cmap("Paired", 12)

        self.colors = []
        self.magnitudes = []
        self.inshape = []

        for event in self.cat:
            self.magnitudes.append(event.magnitudes[0].mag)
            # Use color to Code the different events. Colorcode by event
            # cluster or indicate if an event did not get relocated.
            if event.origins[-1].method_id is None or \
               "HYPODD" not in str(event.origins[-1].method_id).upper():
                self.colors.append(color_invalid)
            # Otherwise get the cluster id, stored in the comments.
            else:
                for comment in event.origins[-1].comments:
                    comment = comment.text
                    if comment and "HypoDD cluster id" in comment:
                        cluster_id = int(comment.split(":")[-1])
                        break
                else:
                    cluster_id = 0
                self.colors.append(cmap(int(cluster_id)))
            self.inshape.append(True)
            if shape:
                if not shape.contains(event.origins[-1].longitude,
                                      event.origins[-1].latitude):
                    self.inshape[-1] = False
                    
    def _plot_events(self, positions, shape,
                     map_extent=None, depth_extent=None):
        """
        Plot event locations as map view and 2 cross-sections

        Uses cartopy
        :param positions:  Positions object
        :param shape:
        :param map_extent:
        :param depth_extent:
        """
        plt.clf()
        mcs = MapCrossSection(map_extent=map_extent,
                              depth_extent=depth_extent,
                              latitudes=positions.latitudes,
                              longitudes=positions.longitudes,
                              depths=positions.depths,
                              fill_figure=False,
                              coastlines=self.coastlines)

        self._plot_2D(mcs.ax_map, positions.longitudes, positions.latitudes,
                      transform=ccrs.Geodetic())
        if shape:
            shape.plot(mcs.ax_map, linestyle='--', linewidth=0.5,
                       transform=ccrs.Geodetic())

        # Latitude cross-section
        self._plot_2D(mcs.ax_zy, positions.depths, positions.latitudes)
        mcs.ax_zy.set_xlabel('Depth (km)')
        mcs.ax_zy.set_ylabel('Latitude')

        # Longitude cross-section
        self._plot_2D(mcs.ax_xz, positions.longitudes, positions.depths)
        mcs.ax_xz.set_xlabel('Longitude')
        mcs.ax_xz.set_ylabel('Depth (km)')

        return mcs.map_extent, mcs.depth_extent

    def _plot_2D(self, ax, xs, ys, ref_mag=None, transform=None):
        """
        Plot a 2D view (map or cross-section)

        :param ax: axes object
        :param xs: x-axis values
        :param ys: y-axis values (same length as xs)
        :param ref_mag: magnitude at which the marker size = marker_size.  If
            None, use marker_size everywhere.
        :param transform: transform to use when plotting (None for
            cross-sections, ccrs.Geodetic() for map view)
        """
        if ref_mag:
            sizes = [self.marker_size*3**(x-ref_mag) for i, x in
                     zip(self.inshape, self.magnitudes) if i is True]
        else:
            sizes = self.marker_size**2
        if transform is None:
            transform = ax.transData
        if self.replace_scatter_with_plot:
            ax.plot(xs, ys, color='#e0e0e0', marker='.', markersize=0.1,
                    linestyle='', transform=transform)
            ax.plot([x for i, x in zip(self.inshape, xs) if i is True],
                    [y for i, y in zip(self.inshape, ys) if i is True],
                    color='k',
                    marker='.',
                    markersize=0.1,
                    linestyle='',
                    transform=transform)
        else:
            ax.scatter(xs, ys, s=sizes, c='#e0e0e0', transform=transform)
            ax.scatter([x for i, x in zip(self.inshape, xs) if i is True],
                       [x for i, x in zip(self.inshape, ys) if i is True],
                       s=sizes,
                       c=[x for i, x in zip(self.inshape, self.colors)
                          if i is True],
                       marker='.',
                       transform=transform)


if __name__ == "__main__":
    catalog_file = 'relocated_events.xml'
    print(f'Reading catalog file {catalog_file}...', end='', flush=True)
    cat = read_events(catalog_file, 'QUAKEML')
    print(f'read {len(cat)} events')
    obj = HypoDDPlotter(cat, map_extent=[45.15, 45.75, -13, -12.6],
                             depth_extent=[0, 50])
    obj.plot(file_base='All', coastlines='10m')
    obj.plot(file_base='main_swarm_EW', coastlines='10m',
             polygon=[[45.3, -12.78],
                      [45.3, -12.82],
                      [45.5, -12.82],
                      [45.5, -12.78]])
    obj.plot(file_base='main_swarm_NS', coastlines='10m',
             polygon=[[45.39, -12.65],
                      [45.39, -12.95],
                      [45.42, -12.95],
                      [45.42, -12.65]])
    obj.plot(file_base='secondary_swarm', coastlines='10m',
             polygon=[[45.50, -12.70],
                      [45.65, -12.80],
                      [45.65, -12.90],
                      [45.50, -12.80]])
