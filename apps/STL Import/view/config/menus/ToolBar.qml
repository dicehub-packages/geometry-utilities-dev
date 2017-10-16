import DICE.App 1.0

ToolBarMenu {
    ToolBarGroup {
        title: "Tools"
        SmallToolBarButton {
            iconName: "Check"
            text: "Show mass properties"
            enabled: app.stl_model.selection.hasSelection > 0
            onClicked: {
                massPropertiesDrawer.open()
                app.getMassProperties()
            }
            MassPropertiesDrawer {
                id: massPropertiesDrawer
            }
        }
    }
}
