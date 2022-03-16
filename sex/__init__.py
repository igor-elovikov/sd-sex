from __future__ import annotations

import os
import sys

sys.path.append(os.path.dirname(__file__))

from settings import get_plugin_icon
from ui.toolbar import SexToolBar

from functools import partial

import sd
import sd.api
import sexparser
from sdutils import qt_mgr
from sd.api.qtforpythonuimgrwrapper import QtForPythonUIMgrWrapper

parser = sexparser.NodeCreator()

def onNewGraphViewCreated(graph_view_id, qt_ui_mgr: QtForPythonUIMgrWrapper):
    # Create our toolbar.
    toolbar = SexToolBar(graph_view_id, qt_ui_mgr, parser)

    # Add our toolbar to the graph widget.
    created_graph = qt_ui_mgr.getGraphFromGraphViewID(graph_view_id)

    if isinstance(created_graph, sd.api.SDSBSFunctionGraph):
        qt_ui_mgr.addToolbarToGraphView(
            graph_view_id,
            toolbar,
            icon = get_plugin_icon("ie-icon.png"),
            tooltip = "Expression Editor")

def initializeSDPlugin():
    qt_mgr.registerGraphViewCreatedCallback(partial(onNewGraphViewCreated, qt_ui_mgr = qt_mgr))
