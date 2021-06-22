import QtQuick 2.10
import QtQuick.Controls.Material 2.3
import QtQuick.Window 2.10
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3


ApplicationWindow{
    visible: true;
    width: 1280;
    height: 720;

    Row{
        spacing: 30;
        Button {
            text: qsTr("Save")

            ToolTip.visible: down
            ToolTip.text: qsTr("Save the active project")
        }
        Button {
            text: qsTr("Button")

            ToolTip.visible: pressed
            ToolTip.delay: Qt.styleHints.mousePressAndHoldInterval
            ToolTip.text: qsTr("This tool tip is shown after pressing and holding the button down.")
        }

        Button {
            text: qsTr("Button")
            hoverEnabled: true

            ToolTip.delay: 1000
            ToolTip.timeout: 5000
            ToolTip.visible: hovered
            ToolTip.text: qsTr("This tool tip is shown after hovering the button for a second.")
        }
        Slider {
            id: slider
            value: 0.5

            ToolTip {
                parent: slider.handle
                visible: slider.pressed
                text: slider.value.toFixed(1)
            }
        }
    }
}