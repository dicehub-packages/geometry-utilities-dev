import QtQuick 2.4
import QtWebEngine 1.3
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4 as QQC1
import QtQuick.Controls 2.2

import DICE.Components 1.0
import DICE.App 1.0

Item {
    property Component toolBar: ToolBarMenu {}

    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent

        property var codeEditorDrawer

        Popup {
            id: popup

            width: 0.5 * appWindow.width
            height: 0.5 * appWindow.height
            x: 0.5 * (parent.width - width)
            y: 0.5 *(parent.height - height)

            TextArea {
                id: errorText
                anchors.fill: parent
            }

            Connections {
                target: app
                onError: {
                    errorText.text = error;
                    popup.open();
                } 
                    
            }
        }

        RowLayout {
            Layout.fillWidth: true

            FlatButton {
                text: "Apply"
                onClicked: {
                    app.saveRequest();
                }
            }

            Label {
                text: 'Output type:'
            }

            DiceInputField {
                width: 300
                target: app
                property: 'outputType'
            }

        }

        QQC1.SplitView {
            Layout.fillHeight: true
            Layout.fillWidth: true
            Item {
                Layout.fillHeight: true
                width: parent.width/2

                WebEngineView {
                    id: codeView

                    anchors.fill: parent

                    settings.localContentCanAccessFileUrls: true
                    settings.errorPageEnabled: true

                    Connections {
                        target: app
                        onSaveRequest: {
                            codeView.runJavaScript("editor.getValue()", function(result) { app.save(result); });
                        } 
                    }

                    Component.onCompleted: {
                        loadHtml('\
                            <!DOCTYPE html>\
                            <html>\
                            <head>\
                              <meta charset="UTF-8">\
                              <style type="text/css" media="screen">\
                                #editor {\
                                    position: absolute;\
                                    top: 0;\
                                    bottom: 0;\
                                    left: 0;\
                                    right: 0;\
                                }\
                              </style>\
                            </head>\
                            <body>\
                            <div id="editor">
                            </div>
                            <script src="src-min/ace.js" type="text/javascript" charset="utf-8"></script>\
                            <script>\
                                var editor = ace.edit("editor");\
                                editor.setTheme("ace/theme/monokai");\
                                editor.session.setMode("ace/mode/python");\
                                editor.setValue('+JSON.stringify(app.script)+', 1);\
                                editor.setShowPrintMargin(false);\
                            </script>\
                            </body>\
                            </html>\
                        ', Qt.resolvedUrl('ace/'));
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.NoButton
                    propagateComposedEvents: true
                    onWheel: {
                        if (wheel.modifiers & Qt.ControlModifier) {
                            var angle = wheel.angleDelta.y
                            if (angle>0) {
                                codeView.zoomFactor += 0.1;
                            }
                            else {
                                codeView.zoomFactor -= 0.1;
                            }   
                        } else {
                            wheel.accepted = false;
                        }

                    }
                }
            }


            Item {
                Layout.fillHeight: true
                Layout.fillWidth: true

                Component.onCompleted: {
                    app.vis.parent = this;
                    app.vis.anchors.fill = this;
                }
            }
        }

    }


}

