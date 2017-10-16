import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQml.Models 2.2
import QtQuick.Window 2.2

import DICE.App 1.0
import DICE.Components 1.0


Item {
    width: parent.width
    height: 30

    Component {
        id: dragIndicator
        Text {
            property variant data: []
        }
    }

    Rectangle {
        anchors.fill: parent
        color: 'orange'
        visible: meshesDropArea.containsDrag || filesDropArea.containsDrag

    }

    DropArea {
        id: meshesDropArea
        anchors.fill: parent
        keys: ['meshes']
        onDropped: {
            moveMeshes(drag.source.data);
        }
    }

    DropArea {
        id: filesDropArea
        anchors.fill: parent
        keys: ['files']
        onDropped: {
            mergeFiles(drag.source.data);
        }
    }

    Item {
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.right: visibleCheck.left
        height: childrenRect.height

        BasicText {
            id: label
            visible: !fileNameText.focus
            anchors.top: parent.top
            anchors.left: parent.left
            text: name
        }

        TextInput {
            id: fileNameText

            visible: focus
            activeFocusOnPress: false
            anchors.top: parent.top
            anchors.left: parent.left
            text: name
            onFocusChanged: {
                if (!focus) {
                    setName(text)
                }
            }
            onEditingFinished: {
                focus = false
            }
        }
    }

    Connections {
        target: delegateRoot
        onDoubleClicked: fileNameText.forceActiveFocus()
    }

    Item {
        id: dragger
        visible: !loading
        enabled: !loading
        width: childrenRect.width
        height: childrenRect.height
        anchors.margins: 5
        anchors.right: visibleCheck.left
        anchors.verticalCenter: parent.verticalCenter
        Grid {
            columns: 3
            columnSpacing: 1
            rowSpacing: 1
            Repeater {
                model: 9
                FontAwesomeIcon {
                    opacity: 0.6
                    size: 1
                    name: "Square"
                }
            }
        }

        MouseArea {
            id: dragArea
            anchors.fill: parent
            cursorShape: Qt.OpenHandCursor
            onPressed: {
                current = true
                var p = label.mapToItem(Window.window.contentItem, 0, 0);
                var indicator = dragIndicator.createObject(Window.window);
                indicator.x = p.x
                indicator.y = p.y
                var model = delegateRoot.ListView.view.model
                var selected = model.selection.selectedIndexes
                var desc = []
                var deselect = []
                for (var i = 0; i < selected.length; i++) {
                    var idx = selected[i];
                    var itemType = model.data(idx, 'type')
                    if (itemType == 'file') {
                        desc.push(model.data(idx, 'name'));
                        indicator.data.push(model.data(idx, 'itemId'));
                    } else {
                        deselect.push(idx);
                    }
                }
                model.selection.selectIndexes(deselect, ItemSelectionModel.Deselect)
                indicator.text = desc.join('\n')
                indicator.Drag.active = true
                indicator.Drag.hotSpot.x = indicator.width/2
                indicator.Drag.hotSpot.y = 0
                indicator.Drag.keys = ['files']
                dragArea.drag.target = indicator
            }

            onReleased: {
                if (!!dragArea.drag.target) {
                    var indicator = dragArea.drag.target
                    indicator.Drag.drop()
                    indicator.Drag.active = false
                    dragArea.drag.target = undefined
                    indicator.destroy()
                }
            }

        }
    }

    MouseArea {
        id: visibleCheck

        width: 20
        height: 20
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        enabled: !loading
        visible: enabled
        FontAwesomeIcon {
            size: 12
            anchors.centerIn: parent
            name: isVisible ? "Eye" : "EyeSlash"
        }
        onClicked: {
            isVisible = ! isVisible
        }
    }

    DiceSpinner {
        running: loading
        visible: loading
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        width: 35
        height: 35
    }
}
