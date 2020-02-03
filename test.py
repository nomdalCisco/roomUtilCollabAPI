import xows
import asyncio

async def start():
    async with xows.XoWSClient('10.10.20.159', username='admin', password='ciscopsdt') as client:
        def callback(data, id_):
            print(f'Feedback (Id {id_}): {data}')
            
        calls_made_on_device = await client.xCommand(['CallHistory', 'Get'])

        return calls_made_on_device

ob = asyncio.run(start())["ResultInfo"]

print(ob)

'''
{"jsonrpc":"2.0",
 "id":"1",
 "result":
     {"status":"OK",
      "Entry": [
                  {"id":0,
                   "CallHistoryId":2,
                   "CallbackNumber":"sip:user@cisco.com",
                   "DisplayName":"user@cisco.com",
                   "StartTime":"2018-11-13T14:44:44",
                   "DaysAgo":141,
                   "OccurrenceType":"NoAnswer",
                   "IsAcknowledged":"Acknowledged",
                   "RoomAnalytics":{}
                   }
                ],
      "ResultInfo":{"Offset":0,"Limit":1}
      }
}
'''
