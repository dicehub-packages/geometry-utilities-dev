import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Dialogs 1.2

import DICE.App 1.0

Dialog {
    id: root

    title: "STL Merge"

    property string filePath: fileName.text

    FileDialog{
        id: directoryDialog

        nameFilters: [ "STL files (*.stl)", "All files (*)" ]
        selectedNameFilter: "STL files (*.stl)"
        selectExisting: false

        onAccepted: {
            fileName.text = fileUrl.toString().replace(/^(file:\/{2,3})/, "") // remove "file://" from the url
        }
    }

    onAccepted: app.mergePatches(filePath)
//    contentItem: itemLoader.item
    contentItem: Body {
        width: 400
        Card {
            expanderVisible: false
            BodyText {
                text: "Please choose file to save."
                horizontalAlignment: Text.AlignHCenter
            }
            Item {
                height: 20
                width: 1
            }

            Row{
                height: 40
                width: parent.width
                spacing: 10

                InputField{
                    id: fileName

                    width: parent.width - 105
                    label: "File"
                }
                FlatButton{
                    id: button
                    width: 100
                    text: qsTr("Select")
                    onClicked: {
                        directoryDialog.open()
                    }
                }
            }

            Row {
                width: parent.width
                spacing: 10
                height: 40

                FlatButton {
                    id: cancelButton

                    width: parent.width/2
                    text: "Cancel"
                    textColor: Qt.lighter(colors.theme["text_color"], 3)
                    color: colors.theme["text_color"]
                    onClicked: {
                        root.reject()
                    }
                }
                FlatButton {
                    id: confirmButton

                    width: parent.width/2
                    text: "OK"
                    onClicked: {
                        root.accept()
                    }
                }
            }
        }
        Keys.onReturnPressed: {
            confirmButton.clicked()
        }
        Keys.onEscapePressed: {
            cancelButton.clicked()
        }
    }
    modality: Qt.WindowModal
}
