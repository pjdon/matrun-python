% Author: Paul Donchenko <pdonchen@uwaterloo.ca>
% License: GPLv3

% set model parameters if they aren't already set by the caller
if ~exist('input_folder', 'var'), input_folder = './data/level_a'; end
if ~exist('output_folder', 'var'), output_folder = './data/level_b'; end
if ~exist('input_file_template', 'var'), input_file_template = '*.tiff'; end
if ~exist('image_adjust_params', 'var'), image_adjust_params = [.2 .3 0; .6 .7 1]; end

% look for files matching template in input folder
file_search_config = fullfile(input_folder, input_file_template);
input_files = dir(file_search_config);
num_input_files = numel(input_files);

if num_input_files <= 0
    % notify if no input files
    disp(str( ...
        'no files matching ', input_file_template, ' in ', input_folder ...
    ));
else
    % create output folder if doesn't exist
    if ~exist(output_folder, 'dir')
       mkdir(output_folder);
       disp(strcat('output folder created at ', output_folder));
    end
    
    % iterate through input files that were found
    for k = 1:num_input_files
        input_file_info = input_files(k);

        % build name and path for each input file
        input_file_name = input_file_info.name;
        input_file_path = fullfile(input_folder, input_file_name);
        
        % read the image data for the current input file
        img_file = Tiff(input_file_path);
        img_data = read(img_file);
        
        % apply image adjustment
        new_img_data = imadjust(img_data, image_adjust_params);
        
        % create output path using input name and output folder
        output_file_path = fullfile(output_folder, input_file_name);
        
        % write adjusted image to output folder
        imwrite(new_img_data, output_file_path);
        disp(strcat('adjusted img written to ', output_file_path));       
        

    end
end
