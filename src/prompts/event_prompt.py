from langchain_core.prompts import PromptTemplate


event_list_prompt = PromptTemplate.from_template("""
Analyze the following text:

# INPUT TEXT 

{input_text}
______________________________________________________

Generate a list of events by extracting information from the provided text, in the following format:
<Events>
    <Event0>
        <title> Event Title </title>
        <start_time> 2025-01-01T20:30:00+01:00 </start_time>
        <end_time> 2025-01-01T22:00:00+01:00 </end_time>
        <location> The O2, Peninsula Square, London SE10 0DX, United Kingdom </location>
    </Event0>
    
    <Event1>
    ...
    </Event1>
</Events>

Instructions: 
- Consider this as today's date: {current_date}
- In the input text, only look for events that have at least a date indication, 
    do not create an event if you don't find its date
- There is no limit on the events to create, if you find counters in text, please ignore
- All datetime values MUST include timezone information (e.g., +01:00 for CET, +02:00 for CEST)
- Use ISO 8601 format with timezone offset: YYYY-MM-DDTHH:MM:SS+TZ:TZ
- If the year is not specified, use current year: {current_year}
- Try to infer the timezone from the context of the input text, in this way:
    1. FIRST, scan the ENTIRE input text for explicit timezone declarations 
       (e.g., "All times are in...", "Times shown in...", "Times in..." page-level timezone indicators).
       These page-level declarations take ABSOLUTE PRIORITY.
    2. If no page-level timezone is found, look for event-specific timezone information.
    3. Only if both options 1. and 2. fail, try to infer timezone from event location.
    4. Always use IANA format. If the input refers to a timezone region 
       (e.g., "Central Europe", "Pacific Time", "CET"), choose the most standard 
       and widely used IANA zone in that region.
           
Do not overdo the task, if you don't find any event, do not generate anything as result.
""")

filter_events_by_user_query_prompt = PromptTemplate.from_template("""
Analyze the following list of events:

# INPUT EVENTS

{event_list}
______________________________________________________

Now filter the events in the list based on the following user query:

# USER QUERY

{user_query}
______________________________________________________

Instructions:
- Consider this as today's date: {current_date} (useful for relative time references, e.g. 'today', 'next weekend', ...)
- The ONLY action you can do is remove elements from the list
- Do NOT consider day of week for the output model
- Absolutely DO NOT add, remove or change any information to events (other than day of week)
- If a user query requires information or context you don't have, just avoid applying any filter
  (e.g. events near my house --> IGNORE, you don't know where the user lives
        events near Milan --> OK, Milan is an absolute reference)
- DO NOT invent, interpret or make assumptions. If you're not sure enough do not apply any filter
""")
