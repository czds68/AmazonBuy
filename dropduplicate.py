import csv
task_file = open('SubmitReviewer.csv', 'r', newline='')
file_info = list(csv.reader(task_file))
production_header = file_info[0]
production_infos = file_info[1:]


task_file = open('reviewout.csv', 'w', newline='')
info_file_write = csv.writer(task_file)
info_file_write.writerow(production_header)
recored = []
for item in production_infos:
    content = [item[0], item[3]]
    if content not in recored:
        recored.append(content)
        info_file_write.writerow(item)
task_file.close()