// static/blockly/custom_blocks.js

Blockly.defineBlocksWithJsonArray([{
    "type": "move_forward",
    "message0": "forward at speed %1",
    "args0": [{
        "type": "field_number",
        "name": "SPEED",
        "value": 20,
        "min": 0,
        "max": 100
    }],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Move robot forward at set speed.",
    "helpUrl": ""
}]);


Blockly.Python['move_forward'] = function(block) {
    var s = block.getFieldValue('SPEED');
    return `robot.forward(${s})\n`;
};


Blockly.defineBlocksWithJsonArray([{
    "type": "move_backward",
    "message0": "backward at speed %1",
    "args0": [{
        "type": "field_number",
        "name": "SPEED",
        "value": 20,
        "min": 0,
        "max": 100
    }],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Move robot backward at set speed.",
    "helpUrl": ""
}]);


Blockly.Python['move_backward'] = function(block) {
    var s = block.getFieldValue('SPEED');
    return `robot.backward(${s})\n`;
};


Blockly.defineBlocksWithJsonArray([{
    "type": "stop",
    "message0": "stop",
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Stop the robot.",
    "helpUrl": ""
}]);


Blockly.Python['stop'] = function(block) {
    return `robot.stop()\n`;
};


Blockly.defineBlocksWithJsonArray([{
    "type": "sleep",
    "message0": "sleep %1 second(s)",
    "args0": [{
        "type": "field_number",
        "name": "SECONDS",
        "value": 1,
        "min": 0,
    }],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Sleep for set seconds.",
    "helpUrl": ""
}]);


Blockly.Python['sleep'] = function(block) {
    var s = block.getFieldValue('SECONDS');
    return `time.sleep(${s})\n`;
};

Blockly.defineBlocksWithJsonArray([{
    "type": "turn",
    "message0": "turn %1 degree(s)",
    "args0": [{
        "type": "field_number",
        "name": "DEGREES",
        "value": 0,
        "min": -30,
        "max": 30
    }],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Turn the front wheels between -30 and 30 degrees.",
    "helpUrl": ""
}]);


Blockly.Python['turn'] = function(block) {
    var d = block.getFieldValue('DEGREES');
    return `robot.set_dir_servo_angle(${d})\n`;
};

Blockly.defineBlocksWithJsonArray([{
    "type": "pan_camera",
    "message0": "pan camera %1 degree(s)",
    "args0": [{
        "type": "field_number",
        "name": "DEGREES",
        "value": 0,
        "min": -30,
        "max": 30
    }],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Pan camera between -30 and 30 degrees.",
    "helpUrl": ""
}]);


Blockly.Python['pan_camera'] = function(block) {
    var d = block.getFieldValue('DEGREES');
    return `robot.set_cam_pan_angle(${d})\n`;
};

Blockly.defineBlocksWithJsonArray([{
    "type": "tilt_camera",
    "message0": "tilt camera %1 degree(s)",
    "args0": [{
        "type": "field_number",
        "name": "DEGREES",
        "value": 0,
        "min": -30,
        "max": 30
    }],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Tilt camera between -30 and 30 degrees.",
    "helpUrl": ""
}]);


Blockly.Python['tilt_camera'] = function(block) {
    var d = block.getFieldValue('DEGREES');
    return `robot.set_cam_tilt_angle(${d})\n`;
};


Blockly.defineBlocksWithJsonArray([{
    "type": "read_distance",
    "message0": "distance (cm)",
    "output": "Number",
    "colour": 230,
    "tooltip": "Read ultrasonic distance in cm.",
    "helpUrl": ""
}]);

Blockly.Python['read_distance'] = function(block) {
    return [`robot.get_distance()`, Blockly.Python.ORDER_ATOMIC];
};


Blockly.defineBlocksWithJsonArray([{
    "type": "read_grayscale",
    "message0": "grayscale values",
    "output": "Array",
    "colour": 230,
    "tooltip": "Get all three grayscale sensor readings.",
    "helpUrl": ""
}]);


Blockly.defineBlocksWithJsonArray([{
    "type": "read_line_status",
    "message0": "line status",
    "output": "Array",
    "colour": 230,
    "tooltip": "Get line status (0 white / 1 black) for left, center, right.",
    "helpUrl": ""
}]);


Blockly.defineBlocksWithJsonArray([{
    "type": "read_cliff",
    "message0": "cliff detected?",
    "output": "Boolean",
    "colour": 230,
    "tooltip": "True if any cliff sensor is triggered.",
    "helpUrl": ""
}]);


Blockly.defineBlocksWithJsonArray([{
    "type": "read_line",
    "message0": "line sensor %1",
    "args0": [{
        "type": "field_dropdown",
        "name": "CHANNEL",
        "options": [
            ["left", "0"],
            ["center", "1"],
            ["right", "2"]
        ]
    }],
    "output": "Number",
    "colour": 230,
    "tooltip": "Read one of the three line sensors.",
    "helpUrl": ""
}]);


Blockly.Python['read_line'] = function(block) {
    const idx = parseInt(block.getFieldValue('CHANNEL'), 10);
    // this will generate a Python expression that indexes into the list
    return [`robot.get_line_status()[${idx}]`, Blockly.Python.ORDER_ATOMIC];
};


Blockly.defineBlocksWithJsonArray([{
    "type": "color_detect",
    "message0": "Color detect %1",
    "args0": [{
        "type": "field_dropdown",
        "name": "COLOR",
        "options": [
            ["red",     "red"],
            ["orange",  "orange"],
            ["yellow",  "yellow"],
            ["green",   "green"],
            ["blue",    "blue"],
            ["purple",  "purple"],
            ["magenta", "magenta"],
            ["off",     "off"]
        ]
    }],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 210,
    "tooltip": "Turn on color detection for selected color, or off to disable.",
    "helpUrl": ""
}]);

// Python code generator
Blockly.Python['color_detect'] = function(block) {
    const color = block.getFieldValue('COLOR');
    if (color === 'off') {
        return `Vilib.close_color_detection()\n`;
    } 

    else {
        return `Vilib.color_detect('${color}')\n`;
    }
};


function makeDetectBlock(type, label) {
    Blockly.defineBlocksWithJsonArray([{
        "type": type,
        "message0": label + " %1",
        "args0": [{
            "type": "field_dropdown",
            "name": "STATE",
            "options": [
                ["on", "TRUE"],
                ["off","FALSE"]
            ]
        }],
        "previousStatement": null,
        "nextStatement": null,
        "colour": 210,
        "tooltip": `Turn ${label.toLowerCase()} detection on or off.`,
        "helpUrl": ""
    }]);

    Blockly.Python[type] = function(block) {
        const st = block.getFieldValue('STATE');
        return `vilib.${type}(${st === 'TRUE'})\n`;
    };
}


makeDetectBlock('face_detect_switch',    'Face detect');
makeDetectBlock('traffic_detect_switch', 'Traffic detect');
makeDetectBlock('qrcode_detect_switch',  'QR detect');
makeDetectBlock('hands_detect_switch',   'Hands detect');
makeDetectBlock('pose_detect_switch',    'Pose detect');
makeDetectBlock('image_classify_switch',    'Image classify');
makeDetectBlock('object_detect_switch',    'Object detect');
