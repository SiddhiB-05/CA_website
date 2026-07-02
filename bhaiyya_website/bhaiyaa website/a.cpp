#include<bits/stdc++.h>
#define ll long long
#define pb push_back
using namespace std;
int main()
{
	ios_base::sync_with_stdio(0);
	cin.tie(NULL);
	int test;
	cin>>test;
	while(test--)
	{
		ll n,k;
		cin>>n>>k;
		vector<ll> a(n);
		for(ll i=0;i<n;i++)
		{
			cin>>a[i];
		}
		vector<ll> sum;
		for(ll i=1;i<n;i++)
		{
			sum.pb(a[i]+a[i-1]);
		}
		sort(sum.begin(),sum.end());
		ll minn=0;
		for(ll i=0;i<k-1;i++)
		{
			minn+=sum[i];
		}
		ll maxx=0;
		for(ll i=sum.size()-1;i>sum.size()-k;i--)
		{
			maxx+=sum[i];
		}
		cout<<maxx-minn<<"\n";
	}
	return 0;
}
