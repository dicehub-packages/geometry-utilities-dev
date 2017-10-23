import QtQuick 2.4
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

import DICE.App 1.0
import DICE.Components 1.0


AppLayoutCard {
    Subheader { text: "History of Actions" }

    DiceScrollView  {
        width: parent.width
        Layout.fillWidth: true
        Layout.fillHeight: true
        ListView {
            id: lview
            width: parent.width
            height: childrenRect.height
            model: app.historyModel
            delegate: historyItemDelegate
        }
    }
    property Component historyItemDelegate: Rectangle {
        width: parent.width
        height: text.implicitHeight + 20
        color: index % 2 ? "#f4f4f4" : "transparent"
        BodyText {
            id: text

            anchors.verticalCenter: parent.verticalCenter
            text: cmd + " " + paramStr
        }
    }
    Item {
        height: 40
        width: parent.width
    }
    Button {
        text: qsTr("clear history")
        Layout.fillWidth: true
        onClicked: app.clearHistory()
    }

    Button {
        text: qsTr("Remove Last Action and Repeat All")
        Layout.fillWidth: true
        onClicked: app.removeLastActionAndReplay()
    }

    Button {
        text: qsTr("Replay History")
        Layout.fillWidth: true
        onClicked: {
            app.replay()
        }
    }

}
