map_center = [59.93428, 30.335098]
map_zoom = 12
gps_image = 'swm/track.png'
msg_path = '/messages/drivers'

functions = [
    'msg_receive',
    'show_regions',
    'show_sgbs',
    'show_routes',
    'show_gps'
    ]

msg_types = [
    'No access to SGB',
    'Traffic jam',
    'Accident on the road',
    'Road works on the route',
    'Breakdown of the car',
    'The car got into an accident',
    'SGB breakdown'
]

msg_period = 5
msg_num = 3
