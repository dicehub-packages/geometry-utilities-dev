import DICE.App 1.0


Body {
    Card {
        header: CenteredImage {
            color: "#03A9F4"
            source: appController.icon
        }
        title: qsTr("Geoemtry Import")
        Subheader { text: qsTr("Description") }
        BodyText {
            text: qsTr("Imports and manipulates STL-Files for further processing.
Every action is recorded in the history so by pushing the Play-Button every step of
the manipulation can be performed again.")
        }
    }
    Card {
        Subheader { text: qsTr("Input") }
        List {
            maxHeight: 300
            width: parent.width
            modelData: app.input_types_model
            delegate: ListItem {
                text: input_type
            }
        }
    }
    Card {
        Subheader { text: qsTr("Output") }
        List {
            maxHeight: 300
            width: parent.width
            modelData: app.output_types_model
            delegate: ListItem {
                text: output_type
            }
        }
    }
}
