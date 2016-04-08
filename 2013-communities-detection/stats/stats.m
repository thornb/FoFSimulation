
% Different community detection algorithms
cpm = importdata('C:\Users\Tommy Nguyen\Desktop\communities\stats\cpm_summary.txt');
ia = importdata('C:\Users\Tommy Nguyen\Desktop\communities\stats\ia_unweighted_summary.txt');
iaw = importdata('C:\Users\Tommy Nguyen\Desktop\communities\stats\ia_weighted_summary.txt');
g = importdata('C:\Users\Tommy Nguyen\Desktop\communities\stats\ganxis_unweighted_summary.txt');
gw = importdata('C:\Users\Tommy Nguyen\Desktop\communities\stats\ganxis_weighted_summary.txt');

% Different selected covers to compare and contrast
cff = importdata('C:\Users\Tommy Nguyen\Desktop\covers\gowalla\new\geofriend_nearest_avg.txt');
% 1: Size, 2: Intra-Edge count

%Intra-density
figure;
hold; 
plot(cpm(:,5), cpm(:,1) ./ (0.5 * cpm(:,5) .* (cpm(:,5) - 1)), 'b+')
plot(ia(:,5), ia(:,1) ./ (0.5 * ia(:,5) .* (ia(:,5) - 1)), 'r+')
plot(iaw(:,5), iaw(:,1) ./ (0.5 * iaw(:,5) .* (iaw(:,5) - 1)), 'c+')
plot(g(:,5), g(:,1) ./ (0.5 * g(:,5) .* (g(:,5) - 1)), 'g+')
plot(gw(:,5), gw(:,1) ./ (0.5 * gw(:,5) .* (gw(:,5) - 1)), 'k+')
plot(cff(:,1), cff(:,2) ./ (0.5 * cff(:,1) .* (cff(:,1) - 1)), 'm+')

xlabel('Community Size')
ylabel('Intra-density')
grid on;
box;
legend('CPM Modified', 'IA Unweighted', 'IA Weighted', 'Ganxis Weighted', 'Ganxis Unweighted', 'CFF Cover')


% Average Spatial Distance
figure;
hold; 

plot(cpm(:,5), log(cpm(:,3)), 'b+')
plot(ia(:,5), log(ia(:,3)), 'r+')
plot(iaw(:,5), log(iaw(:,3)), 'c+')
plot(g(:,5), log(g(:,3)), 'g+')
plot(gw(:,5), log(gw(:,3)), 'k+')
plot(cff(:,1), log(cff(:,10)), 'm+')

box on;
grid on;

legend('CPM Modified', 'IA Unweighted', 'IA Weighted', 'Ganxis Weighted', 'Ganxis Unweighted', 'CFF Cover')
xlabel('Community Size')
ylabel('ASD (Log-scale)')

% Spatial Diameter
figure;
hold; 
plot(cpm(:,5), log(cpm(:,4)), 'b+')
plot(ia(:,5), log(ia(:,4)), 'r+')
plot(iaw(:,5), log(iaw(:,4)), 'c+')
plot(g(:,5), log(g(:,4)), 'g+')
plot(gw(:,5), log(gw(:,4)), 'k+')
plot(cff(:,1), log(cff(:,8)), 'm+')
box on;
grid on;
legend('CPM Modified', 'IA Unweighted', 'IA Weighted', 'Ganxis Weighted', 'Ganxis Unweighted', 'CFF Cover')
xlabel('Community Size')
ylabel('Spatial Diameter (Log-scale)')
