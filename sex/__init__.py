from __future__ import annotations

import os
import sys
import logging

sys.path.append(os.path.dirname(__file__))

from ui.toolbar import SexToolBar

from functools import partial

import sd
import sd.api
from sdutils import qt_mgr, ctx
from sd.api.qtforpythonuimgrwrapper import QtForPythonUIMgrWrapper

from settings import get_plugin_icon

logger = logging.getLogger("sd-sex")
logger.handlers = [ctx.createRuntimeLogHandler()]
logger.propagate = False

def onNewGraphViewCreated(graph_view_id, qt_ui_mgr: QtForPythonUIMgrWrapper):
    # Create our toolbar.
    toolbar = SexToolBar(graph_view_id, qt_ui_mgr)

    # Add our toolbar to the graph widget.
    created_graph = qt_ui_mgr.getGraphFromGraphViewID(graph_view_id)

    if isinstance(created_graph, sd.api.SDSBSFunctionGraph) or isinstance(created_graph, sd.api.SDSBSCompGraph):
        qt_ui_mgr.addToolbarToGraphView(
            graph_view_id,
            toolbar,
            icon = get_plugin_icon("ie-icon.png"),
            tooltip = "Expression Editor")

def initializeSDPlugin():
    qt_mgr.registerGraphViewCreatedCallback(partial(onNewGraphViewCreated, qt_ui_mgr = qt_mgr))
