'''
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''

# Need to do a 'pip install exchangelib' to get the library installed.
# I don't have necessary permissions to access the Exchange Server, so this is difficult to test

# Import the Python library for Microsoft Exchange
from exchangelib import Credentials, Account, EWSDateTime
from datetime import timedelta

# Import the Cisco Python library for Cisco Collaboration Endpoint XAPI over WebSockets
import xows
import asyncio

# Import for comparing datetimes to one another
import dateutil.parser
import datetime

##################################### Enter User, Rooms, and Dates Informatiomn #####################
user_email = 'ENTER EMAIL ADDRESS'
user_password = 'ENTER PASSWORD'

company_name = 'ENTER COMPANY NAME'

# This list could be hard-coded or it could be pulled from somewhere else (as it's likely a lot of information) and
# created using a super simple Python script. These would be strings of the room addresses (ex: 'conferenceRoomA@company.com')
# which correspond to the room mailboxes in Exchange--where we will be pulling the calendar information from, and which
# are mapped to lists consisting of of the Cisco endpoint IP addresses (ex: '1.2.3.4') that represent the endpoint in that room
# followed by the endpoint's username and then its password. My understanding of how this works may need adjusting.
# If we want to handle cases where there are multiple endpoints in a room, we could use a list of IP addresses.
# Unsure if more rich info is needed to achieve what we're using this for.
map_of_endpoint_ip_addresses_to_rooms = {'Room Address': ['Endpoint IP Address', 'Endpoint Username', 'Endpoint Password']}

# This list is derived from the above mapping and used to iterate over each room
list_of_meeting_room_addresses = map_of_endpoint_ip_addresses_to_rooms.keys()

# Enter the range of dates to search for data over
start_year = 'ENTER END YEAR'
start_month = 'ENTER START YEAR'
start_day = 'ENTER START DAY'

start_date = datetime.date(int(start_year), int(start_month), int(start_day))

end_year = 'ENTER END YEAR'
end_month = 'ENTER END MONTH'
end_day = 'ENTER END DAY'

end_date = datetime.date(int(end_year), int(end_month), int(end_day))

# Count the total number of meetings that happened in all the rooms during the time range
meeting_count = 0

# Count the number of meetings that did not involve an endpoint in the reserved room,
# and thus may not have happened
potentially_did_not_occur = 0

# Count the number of calls that were placed during scheduled meetings
calls_placed_during_scheduled_meetings = 0

#####################################################################################################

def main():

    credentials = Credentials(user_email, user_password)
    account = Account(user_email, credentials=credentials, autodiscover=True)

    # For this to work, the current user must have proper access granted to the rooms.
    # It is common to have access_type=IMPERSONATION as a default, in which case this
    # should be added to the login below

    # Iterate through all of the rooms being examined
    for room in list_of_meeting_room_addresses:
        
        room_account = Account(primary_smtp_address=room, credentials=my_credentials)
        
        start_date = room_account.default_timezone.localize(EWSDateTime(int(start_year), int(start_month), int(start_day)))
        end_date = room_account.default_timezone.localize(EWSDateTime(int(end_year), int(end_month), int(end_day)))

        # Get the current room's calendar
        current_room_calendar = room_account.calendar

        # Get the info for endpoint(s) present in the room
        current_room_endpoint_info = map_of_endpoint_ip_addresses_to_rooms[room]

        current_room_endpoint_ip = current_room_endpoint_info[0]
        current_room_endpoint_username = current_room_endpoint_info[1]
        current_room_endpoint_password = current_room_endpoint_info[2]

        # Get the events on the room's calendar by the dates being examined
        # Use this method instead of 'filter' because we want every recurring meeting too,
        # not just the master
        all_meetings = current_room_calendar.view(
            start=start_date,
            end=end_date) + timedelta(days=1)

        # Add the total number of meetings that occured within the timeframe in this specific room
        # to the total meeting count
        meeting_count += len(all_meeetings)

        for meeting in all_meetings:

            # Get the current meeting's times, I think it is formatted yyyy-MM-dd'T'HH:mm:ss
            current_meeting_start_time = meeting.start
            current_meeting_end_time = meeting.end

            # This function call should return a dictionary object containing all the endpoint's call-logs, ideally over
            # the defined period. We get the actual list of calls made on the device, which are represented as dictionary objects,
            # by referencing the dictionary at 'Entry'
            list_of_calls_on_device = asyncio.run(start(current_room_endpoint_ip, current_room_endpoint_username, current_room_endpoint_password))['Entry']

            # Reset variable to check whether a call was placed on endpoint during meeting
            meeting_had_call = False
            
            # Iterate through all of the calls placed on the device. This is massively inefficient but I'm building from here
            for call in list_of_calls_on_device:

                # The time the current call was placed, formatted yyyy-MM-dd'T'HH:mm:ss
                time_call_placed = call["StartTime"]


                datetime.datetime(2019, 7, 2,23,15,9)

                # This may not work as planned and need some fidgiting, as I'm not 100% sure on the current format of datetimes
                # This should result in the following times formatted in a form that Python can compare
                time_placed_converted = dateutil.parser.parse(time_call_placed)
                start_time_converted = dateutil.parser.parse(current_meeting_start_time)
                end_time_converted = dateutil.parser.parse(current_meeting_end_time)

                # Check whether the current call was placed between the start and end times of the current meeting on the calendar
                if time_to_check < end_time_converted and time_to_check > start_time_converted:

                    # If this hits, that means a call was placed on the endpoint in the current room during a meeting scheduled
                    # during this time. Thus, save this information.
                    calls_placed_during_scheduled_meetings += 1
                    meeting_had_call = True

                    # No need to log multiple calls placed during the same meeting
                    break

            # Once all calls have been checked to see if they occured during the meeting, we know whether or not
            # to log a meeting that potentially didn't take place
            if not meeting_had_call:
                potentially_did_not_occur += 1

# Could get around doing it this way and not need the username or password, could just use the WebEx APIs where I take the user/org and get
# all of the associated device IDs and then use the xAPI WebEx API command for getting the CallHistory for the given device IDs--no IP needed

# Checkout the hybrid connector API on WebEx
# Helper function called to return the call logs for a given endpoint
async def start(endpoint_ip, endpoint_username, endpoint_password):
    async with xows.XoWSClient(endpoint_ip, username=endpoint_username, password=endpoint_password) as client:p
    
        # Note: This will retrieve 65534 entries by default if no limit is set
    calls_made_on_device = await client.xCommand(['CallHistory', 'Get'])

    return calls_made_on_device

if __name__ == '__main__':
    main()
    print("At " + company_name + " in " + str(len(list_of_meeting_room_addresses)) + " different meeting rooms over the period ", \
          "from " + str(start_date) + " to " + str(end_date) + " there were " + str(meeting_count) + " meetings held, and of those ", \
        "meetings, " + str(calls_placed_during_scheduled_meetings) + "(" + str(calls_placed_during_scheduled_meetings/meeting_count) + "%)", \
        " of them had calls placed on the scheduled room's endpoint during the scheduled meeting times, and " + str(potentially_did_not_occur) + "(", \
        + str(potentially_did_not_occur/meeting_count) + "%)" " did not.")

# The output of this would look something like this:

# "At Company A in 100 different meeting rooms over the period from 10/9/2018 to 12/9/2018 there were 2000 meetings held, and of those
#  meetings, 1800 (90%) of them had calls placed on the scheduled room's endpoint during the scheduled meeting times, and 200 (10%) did not."







    
