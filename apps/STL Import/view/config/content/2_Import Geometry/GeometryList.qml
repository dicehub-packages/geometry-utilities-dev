import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQml.Models 2.2

import DICE.App 1.0

Item {

    SimpleTreeView {
        id: treeView
        anchors.fill: parent
        model: app.stl_model
        delegate: GeometryListDelegate {}
    }

    DropArea {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.right: parent.right
        height: 50
        onEntered: {
            var prevFlickDeceleration = treeView.flickableItem.flickDeceleration;
            treeView.flickableItem.flickDeceleration = 0;
            treeView.flickableItem.flick(0, 200);
            treeView.flickableItem.flickDeceleration = prevFlickDeceleration;
            drag.accepted = false;
        }
        onPositionChanged: drag.accepted = false
        onDropped: drag.accepted = false
    }

    DropArea {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        height: 50
        onEntered: {
            var prevFlickDeceleration = treeView.flickableItem.flickDeceleration;
            treeView.flickableItem.flickDeceleration = 0;
            treeView.flickableItem.flick(0, -200);
            treeView.flickableItem.flickDeceleration = prevFlickDeceleration;
            drag.accepted = false;
        }

        onPositionChanged: drag.accepted = false
        onDropped: drag.accepted = false
    }
}
