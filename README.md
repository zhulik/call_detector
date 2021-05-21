# call_detector

_call_detector_ listens to microphone and camera states to detect if the user is participating in an online call.
Gathered information is being published to an MQTT broker.

## Where it works

Currently only Linux is supported, I don't have plans to support other operating systems.
If you're interested, feel free to open a PR.

In order to use _call_detector_ you'll need `pulseaudio` or `pipewire-pulse` and `libpulse`.

## How it works

_call_detector_ listens to pulseadio events to detect apps which use the microphone and uses inotify with
some /proc magic to find apps which use the camera.

## MQTT

_call_detector_ was only tested against [mosquitto](https://mosquitto.org/) MQTT broker with login/password authentication and TLS
enabled, however in therory it can work without TLS and authentication and against any broker supported by
[gmqtt](https://github.com/wialon/gmqtt).

Every time the _call_detector_ detects an app which starts or stops using the microphone or the camera,
it publishes a message to an MQTT topic with name of the format `call_detector/<hostname>` where hostname is the hostname
of the machine where you run _call_detector_. Also it sends a message on start and every minute.

Message examples:

`{"camera": [], "microphone": [], "call": false}` when camera and microphone are not active.

`{"camera": ["firefox"], "microphone": ["firefox"], "call": true}` when user is in an online call using firefox.

## Installation

`pip install call_detector`

## Usage

Basic usage:

`call_detector -H mqtt.example.com -U user -P password`

More advanced options can be found in `help`

`call_detector --help`

## Home Assistant

Binary sensor:

```yaml
binary_sensor:
  - platform: mqtt
    name: "User in an online meeting"
    state_topic: "call_detector/<hostname>" # check call_detector --help to find the default topic for your computer
    value_template: "{{ 'ON' if value_json.call else 'OFF' }}"
    json_attributes_topic: "call_detector/<hostname>" # same as state_topic
    json_attributes_template: "{{ value_json | tojson }}"
```

Automation example:

```yaml
- alias: Pause music while User is in an online meting
  trigger:
    - platform: state
      entity_id: binary_sensor.user_in_an_online_meeting
      to: "on"

  condition:
    - condition: state
      entity_id: media_player.mpd
      state: "playing"

  action:
    - service: media_player.media_pause
      data:
        entity_id: media_player.mpd

    - wait_for_trigger:
        - platform: state
          entity_id: binary_sensor.user_in_an_online_meeting
          to: "off"

    - service: media_player.media_play
      data:
        entity_id: media_player.mpd
```

## Contribution

You know;)
