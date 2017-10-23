import QtQuick 2.5 as QQ
import QtQuick.Layouts 1.3 as QQL

import DICE.App 1.0


AppLayoutCard {
    id: root
    
    function checkRowCount() {
        stlTable.visible = app.stl_model.rowCount() > 0
        stlTree.visible = app.stl_model.rowCount() > 0
    }

    GeometryList {
        QQL.Layout.fillWidth: true
        QQL.Layout.fillHeight: true
    }

    QQ.Row {
        spacing: 10
        QQL.Layout.fillWidth: true

        Button {
            text: "Import"
            width: (parent.width - parent.spacing)/2
            onClicked: {
                fileDialog.open(app.addSTL, "Select Files for import",
                                [ "STL File (*.stl)"], true)
            }
        }
        Button {
            text: "Delete selected"
            color: colors.theme['background_color_warning']
            textColor: "#fff"
            width: (parent.width - parent.spacing)/2
            onClicked: {
                app.deleteSelected()
            }
        }
    }
}
