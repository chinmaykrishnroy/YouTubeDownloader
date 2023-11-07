public class sjf
{
public static void main(String[] args)
{
int n = 4;
int t = 0;
int st = 0;
float avgwt = 0;
float avgta = 0;
int[] pid = {1,2,3,4};
int[] at = {0,2,1,4};
int[] bt = {5,3,4,1};
int[] f = new int[n];
int[] ct = new int[n];
int[] ta = new int[n];
int[] wt = new int[n];
for(int i=0; i<n; i++)
f[i] = 0;
while(true)
{
int c=n, min=999;
if(t==n) break;
for (int i=0; i<n; i++)
{
if ((at[i] <= st) && (f[i] == 0) && (bt[i]<min))
{
min = bt[i];
c = i;
}
}
if (c==n)
st++;
else
{
ct[c] = st + bt[c];
st += bt[c];
ta[c] = ct[c] - at[c];
wt[c] = ta[c] - bt[c];
f[c] = 1;
t++;
}
}
for (int j=0; j<n; j++)
{
avgwt += wt[j];
avgta += ta[j];
}
avgwt /= n;
avgta /= n;
System.out.println("\n\tprocess\tAT\tBT\tWT");
for (int i=0; i<n; i++)
{
System.out.println("\t"+pid[i]+"\t"+at[i]+"\t"+bt[i]+"\t"+wt[i]);
}
System.out.println("\nAverage waiting time is: " + avgwt);
System.out.println("Average turnaround time is: " + avgta);
}
}