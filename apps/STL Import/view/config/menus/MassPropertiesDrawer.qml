import DICE.App 1.0

import DICE.Components 1.0 as DC
import QtQuick 2.7 as QQ

Drawer {
    id: root

    width: 0.4 * appWindow.width
    height: appWindow.height

    Card {
        id: card

        title: "Mass Properties"

        header: QQ.Rectangle {
            height: 40
            width: parent.width
            color: "transparent"
            DC.SubheaderText {
                text: appController.name
                anchors.centerIn: parent
            }

            DC.DiceIconButton {
                anchors.right: parent.right
                height: 40
                iconName: "Close"
                color: colors.theme["text_color_subtle"]
                flat: true
                onClicked: {
                    root.close()
                }
            }
        }
        Subheader {
            text: "Volume"
        }
        DiceInputField {
            readOnly: true
            value: app.selectedGeometryVolume
        }
        Subheader {
            text: "Center of gravity"
        }
        DiceVectorField {
            targetValue: app.selectedGeometryCOG
        }
        Subheader {
            text: "Intertia matrix at the center of gravity"
        }
        DiceVectorField {
            xLabel: "xx"
            yLabel: "xy"
            zLabel: "xz"
            targetValue: app.selectedGeometryIntertiaMatrix[0]
        }
        DiceVectorField {
            xLabel: "yx"
            yLabel: "yy"
            zLabel: "yz"
            targetValue: app.selectedGeometryIntertiaMatrix[1]
        }
        DiceVectorField {
            xLabel: "zx"
            yLabel: "zy"
            zLabel: "zz"
            targetValue: app.selectedGeometryIntertiaMatrix[2]
        }
    }
}
