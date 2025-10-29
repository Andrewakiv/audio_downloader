import tasks

result = tasks.process_audio.delay(4, 4, 'https://youtu.be/swfqXNxNCxc?si=bqUnknU3p0lyc0Db')
#delay() is used to call a taskprint(result.ready())
#ready() returns whether the task has finished processing or not.print(result.get(timeout=1))
#get() is used for getting resultsresult.get(propagate=False)
#In case the task raised an exception, get() will re-raise the exception, but you can override this by specifying the propagate argument
# print(result.ready())
# print(result.get(timeout=40))

# result = tasks.first_task.delay(5, 3)