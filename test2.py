import csv
task_file = open('SubmitReviewer.csv', 'r', newline='')
file_info = list(csv.reader(task_file))
production_header = file_info[0]
production_infos = file_info[1:]


task_file = open('review.csv', 'r', newline='')
file_info = list(csv.reader(task_file))
production_header = file_info[0]
production_infos1 = file_info[1:]

task_file = open('reviewout.csv', 'w', newline='')
info_file_write = csv.writer(task_file)
info_file_write.writerow(production_header)
for item in production_infos1:
    test = True
    for item1 in production_infos:
        if item[0] == item1[0] and item[4] == item1[4]:
            test = False
            break
    if test:
        info_file_write.writerow(item)
task_file.close()