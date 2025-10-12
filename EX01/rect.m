%% squarewave_spectrum.m
% Spectrum of a 50 Hz square wave

clear; close all; clc;

% Parameters
A = 2.5;              % amplitude
f0 = 50;            % fundamental frequency [Hz]
T0 = 1/f0;          % period
fs = 5000;          % sampling frequency [Hz]
n_periods = 20;
t = 0:1/fs:n_periods*T0;

%% Generate time-domain signal
x = A * square(2*pi*f0*t);   % 50% duty cycle square wave

%% Compute FFT
N = length(x);
X = fft(x)/N;                  % normalize
f = (-N/2:N/2-1)*(fs/N);       % frequency axis
Xshift = fftshift(X);

% %% Plot time-domain signal
% figure('Name','Square Wave Spectrum','NumberTitle','off');
% subplot(2,1,1);
% plot(t, x, 'LineWidth', 1.2);
% xlabel('Time [s]');
% ylabel('Amplitude');
% title('Square Wave (50 Hz, 50% Duty)');
% grid on;
% xlim([0 2*T0]);

%% Theoretical line spectrum (odd harmonics)
nHarm = 15;  % number of harmonics to show (1,3,5,...)
k = 1:2:nHarm;                    % odd harmonics
harmonics = f0 * k;               % frequency positions
Ak = (4*A/pi) * (1./k);           % amplitudes

%% Plot magnitude spectrum (FFT)
% subplot(2,1,2);
% plot(f, abs(Xshift), 'LineWidth', 1);
% hold on;
% stem(harmonics, Ak, 'r', 'filled');
% xlabel('Frequency [Hz]');
% ylabel('|X(f)|');
% title('Magnitude Spectrum of Square Wave');
% legend('Numerical FFT','Theoretical Harmonics (odd only)');
% grid on;
% xlim([0 1000]);

om = linspace(0, 100, 800);
T_hp = abs(1./(1+2*pi*7./(om*1i)));


figure('Name', 'Spektrum eines Periodischen Rechtecksignals')
% subplot(3,1,1)
stem(harmonics, Ak, 'b', 'filled');
fontsize(20,"points")
title('Spektrum des periodischen Rechtecksignals')
ylabel('Amplitude / V');
xlabel('Frequenz / Hz');




