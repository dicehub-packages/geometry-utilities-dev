import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQml.Models 2.2
import QtQuick.Window 2.2

import DICE.App 1.0
import DICE.Components 1.0


MouseArea {
    id: delegateRoot

    width: parent.width
    height: delegateLoader.height

    drag.smoothed: false
    hoverEnabled: true

    property bool touched: false

    onPressed: {
        ListView.view.forceActiveFocus();
        if (!selected) {
            touched = true;
            current = true;
        }
    }

    onReleased: {
        if (!drag.target && containsMouse && !touched) {
            current = true;
        }
        touched = false
    }

    Rectangle {
        id: background
        anchors.fill: parent
        color: selected ? "lightsteelblue" : "transparent"
    }

    MouseArea {
        id: expandButton
        width: 20
        height: 20
        anchors.verticalCenter: parent.verticalCenter
        visible: hasChildren
        enabled: hasChildren
        x: depth * 20
        FontAwesomeIcon {
            size: 12
            anchors.centerIn: parent
            name: expanded ? "AngleDown" : "AngleRight"
        }
        onClicked: expanded = !expanded
    }

    Loader {
        id: delegateLoader
        anchors.left: expandButton.right
        anchors.right: parent.right
        height: !!item ? item.height : 0
        source: type == 'file' ? 'FileItem.qml' : 'MeshItem.qml'
    }
}

