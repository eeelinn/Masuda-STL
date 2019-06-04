% Original Author:
% Erikka Linn
% May 27, 2019
% Masuda STL, UC San Diego Orthopedic Sugery Dept.
% This program rotates and crops images based on user input.

% Set up environment, close all windows
close all
clearvars

global width height imtype saveDir
width = 1600;
height = 400;
imtype = 'tif';
saveDir = 'cropped';

% Single Image or multiple
helpChoice = questdlg('Select Processing Style to crop (only 1 image vs. multiple images)', ... 
        'Batch or Single', ...
        'Single (select image)','Batch (select folder of images)','Batch (select folder of images)');

switch helpChoice
   case 'Single (select image)'
       % Get File
       [file, path] = uigetfile("*." + imtype, 'Select an Image');
       cd(path)
       I = cropPic([path file]);
       imsave(file, I)
   case 'Batch (select folder of images)'
       % Get Directory 
       cropPics();
end

function C = cropPic(image)
    global width height
    I = imread(image);
    imshow(image, 'Border', 'tight');
    
    %User selects two points (left and right) to level image, main section
    %to keep should be in the middle.
    %User selects a third point which will be labeled accordingly
    [x, y] = getpts;
    
    %T = insertText(I, [x(3) y(3)+50], label,'TextColor', 'cyan', 'Font', 'Courier New Bold', 'FontSize', 30, 'BoxOpacity', 0); 
    
    %Calculate rotation angle and rotate image
    theta = atan((y(2) - y(1))/(x(2) - x(1))) * 180 / pi;
    J = imrotate(I, theta);
    
    % Calculate crop area and crop
    minX = x(3) - width / 2;
    minY = (y(2) + y(1) - height) / 2;
    
    C = imcrop(J, [minX, minY, width, height]);
    imshow(C);
end

function cropPics()
    global imtype
    dirname = uigetdir;
    files = dir("*." + imtype);
    numfiles = length(files);

    for i=1:numfiles
    % Open File
    cd(dirname);
    fullFileName = files(i).name;
    fullPath = [dirname '\' fullFileName];
    
    C = cropPic(fullPath);
    imsave(fullFileName, C);
    end
end

function imsave(file, image)
    global imtype saveDir
    mkdir(saveDir);
    cd(saveDir);
    name = erase(file,"." + imtype);
   
    labels = regexp(name, '_', 'split');
    outstr = strcat('Experiment: ', labels(1), ' Rabbit: ', labels(2), ' Time: ', labels(3));
    
    T = insertText(image, [10 10], outstr, 'TextColor', 'cyan', 'Font', 'Courier New Bold', 'FontSize', 30, 'BoxOpacity', 0);
    imshow(T);
    
    saveFile = strcat(name, "_crop." + imtype);
    imwrite(T, saveFile, imtype);
end