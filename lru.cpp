#include<iostream> 
using namespace std; 
int lru(int time[], int n){ int i, min = time[0], pos = 0; 
for(i = 1; i < n; ++i) 
{ 
if(time[i] < min) 
{ 
min = time[i]; 
pos = i; 
} } 
return pos; 
} 
int main() 
{ 
int frameno, pageno=20, frames[10], page[30], count = 0, time[10], 
flag1, flag2, i, j, pos, pf = 0,hit=0; 
cout<<"Enter number of frames: "; 
cin>>frameno; 
cout<<"Enter 20 pages: "; for(i = 0; i < pageno; ++i) 
{ 
cin>>page[i]; 
} 
for(i = 0; i < frameno; ++i) 
{ 
frames[i] = -1; 
} 
for(i = 0; i < pageno; ++i) 
{ 
flag1 = flag2 = 0; 
for(j = 0; j < frameno; ++j) 
{ 
if(frames[j] == page[i]) 
{ 
count++; hit++; time[j] = count; flag1 = flag2 = 1; break; 
} } 
if(flag1 == 0) 
{ 
for(j = 0; j < frameno; ++j) 
{ 
if(frames[j] == -1) 
{ 
count++; pf++; frames[j] = page[i]; time[j] = count; flag2 = 1; 
break; 
} } } 
if(flag2 == 0) 
{ 
pos = lru(time, frameno); count++; pf++; frames[pos] = page[i]; 
time[pos] = count; 
} } 
cout<<"\n\nNumber of Page Faults "<<pf; cout<<"\nNumber of page 
hits "<<hit<<"\n"; 
return 0;
}