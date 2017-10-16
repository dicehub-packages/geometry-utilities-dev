import QtQuick 2.4
import QtQuick.Controls 1.3

Item {
    property Action surfaceSplitByPatch: Action {
        text: "surfaceSplitByPatch"
        shortcut: ""
        tooltip: "Writes regions of triSurface to separate files."
        iconSource: "images/surfaceSplitByPatch.svg"
        enabled:  app.stl_model.selection.hasSelection > 0
        iconName: text
        onTriggered: app.splitSelected()
    }
}
