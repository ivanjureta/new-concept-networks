# Functions to print to text files

# Print text to text file.
def print_to_txt(file_content, project_name, content_description, save_to_project_dir = False):
    import os
    from tabulate import tabulate
    output_file_name = project_name + '_' + content_description + '.txt'
    if save_to_project_dir == False:
        with open(output_file_name, "w") as text_file:
            print(tabulate(file_content, tablefmt="pipe"), file=text_file)
    else: 
        os.chdir(project_name)
        with open(output_file_name, "w") as text_file:
            print(file_content, file=text_file)
        os.chdir('..')
