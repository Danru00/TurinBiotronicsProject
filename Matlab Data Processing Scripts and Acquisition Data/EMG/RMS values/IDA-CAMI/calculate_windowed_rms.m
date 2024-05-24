%Function that calculates RMS value of a signal in overalpping windows

function [rms_values, num_windows] = calculate_windowed_rms(normalized_signal, window_size, fc)

  window_samples = round(window_size * fc / 1000);  %number of samples per window based on window size and fc
  
  num_windows = floor(length(normalized_signal) / window_samples); %number of windows (considering non-overlapping portions)

  rms_values = zeros(1, num_windows); %Pre-allocate an array to store RMS values

  % Loop through each window and calculate RMS
  for i = 1:num_windows
    start_idx = (i - 1) * window_samples + 1;
    end_idx = min(i * window_samples, length(normalized_signal)); % Ensures end_idx doesn't exceed signal length
    rms_values(i) = rms(normalized_signal(start_idx:end_idx));
  end
  
end
