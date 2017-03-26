# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import json
import pandas as pd
import numpy as np
import seaborn
import requests

leagueIDs=['XXXXXX', 'XXXXXX'] #<---Input your league IDs

for leagueID in leagueIDs:

    #*******************************************************************************************
    #Extract information from each team and put into dataframe
    #*******************************************************************************************

    leagueInfo=requests.get('https://fantasy.premierleague.com/drf/leagues-classic-standings/'+leagueID).json()
    teamList=[]
    n_players=len(leagueInfo['standings']['results'])
    for i in range(0,n_players):
        teamList.append(leagueInfo['standings']['results'][i]['entry']) #List of teams in league
    
    df=pd.DataFrame()
    for teamID in teamList:
        foo=requests.get('https://fantasy.premierleague.com/drf/entry/'+str(teamID)+'/history').json()
        fields=[u'event',u'points',u'points_on_bench',u'rank',u'event_transfers',u'event_transfers_cost',
                u'total_points',u'overall_rank',u'value']
        dfTemp=pd.DataFrame(foo[u'history'],columns=fields)
        teamName=foo['entry'][u'player_first_name']+' '+foo['entry'][u'player_last_name']
        dfTemp.insert(0,'Name',teamName)
        df=df.append(dfTemp)

    nGW=foo[u'history'][-1][u'event']  #Total no. of gameweeks

    df.columns = ['Name','GW','Gameweek Points','Points Bench','Gameweek Rank','Transfers made',
                  'Transfer Cost','Overall Points','Overall Rank','Team Value'] #Renaming columns before plotting

    df=df.reset_index() #Must be done in order to rank
    df['League Rank'] = df.groupby(df['GW'])['Overall Points'].rank(ascending=False,method='min')
    del df['index']
    
    df['Team Value']=df['Team Value']/10
    
    #Set gameweek as index (not necessary but may be helpful):
    df.insert(1,'GW_temp',df['GW'])
    df.set_index('GW',inplace=True)
    df.index=df.index.map(int)
    df.rename(columns={'GW_temp': 'GW'}, inplace=True)

    #Export to csv for use in plotly_fpl.py (which also could be integrated into this script)
    df.to_csv('df.csv', encoding='utf-8')

    #**********************************************************
    #Plotting
    #**********************************************************
    
    g=df.groupby('Name',sort=False)
    dfp=g.last() #Dataframe for plotting e.g. some scatter plots
    rgbs=np.linspace(0.01,1,len(teamList)) #Colors for plotting
    
    ##****************  Overall Points (bar) ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    overall_points=g['Overall Points'].max()
    overall_points.plot(kind='bar',width=1,color=plt.cm.Paired(rgbs))
    plt.xlabel('')
    plt.ylabel('Overall Points')
    plt.xticks(rotation=45,ha='right')
    plt.title('Overall Points after Gameweek %i'%nGW)
    plt.savefig('Overall_Points_bar_%s.png' %leagueID, bbox_inches='tight')
    plt.close()
    
    ##****************  Points bench (bar) ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    overall_points=g['Points Bench'].sum()
    overall_points.plot(kind='bar',width=1,color=plt.cm.Paired(rgbs))
    plt.xlabel('')
    plt.ylabel('Points Bench')
    plt.xticks(rotation=45,ha='right')
    plt.title('Points on bench after Gameweek %i'%nGW)
    plt.savefig('Points_on_bench_bar_%s.png' %leagueID, bbox_inches='tight')
    plt.close()
    
    ##**************** Team Value ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    i=0
    for key,group in g:
        plt.plot(group['GW'],group['Team Value'],'.-',lw=2,markersize=10,label=key,color=plt.cm.Paired(rgbs[i]))
        i=i+1
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlim(0.9,nGW+0.1)
    plt.xticks(range(1,nGW+1))
    plt.xlabel('Gameweek')
    plt.ylabel('Team Value')
    plt.savefig('Team_Value_%s.png' %leagueID, bbox_inches='tight')
    plt.close()
    
    ##****************  Overall Rank ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    i=0
    for key,group in g:
        plt.plot(group['GW'],group['Overall Rank'],'.-',lw=2,markersize=10,label=key,color=plt.cm.Paired(rgbs[i]))
        i=i+1
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlim(0.9,nGW+0.1)
    plt.xticks(range(1,nGW+1))
    plt.xlabel('Gameweek')
    plt.ylabel('Overall Rank')
    plt.gca().invert_yaxis()
    plt.savefig('Overall_Rank_%s.png' %leagueID, bbox_inches='tight')
    plt.close()
    
    ##****************  Transfers made ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    transfers_made=g['Transfers made'].sum()
    transfers_made.plot(kind='bar',width=1,color=plt.cm.Paired(rgbs))
    plt.xlabel('')
    plt.ylabel('Overall Points')
    plt.ylabel('Transfers made')
    plt.xticks(rotation=45,ha='right')
    plt.title('Total transfers made after Gameweek %i'%nGW)
    plt.savefig('Transfers_made_%s.png' %leagueID, bbox_inches='tight')
    plt.close()
    
    ##****************  Transfer Cost ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    transfers_made=g['Transfer Cost'].sum()
    transfers_made.plot(kind='bar',width=1,color=plt.cm.Paired(rgbs))
    plt.xticks(rotation=45,ha='right')
    plt.xlabel('')
    plt.ylabel('Overall Points')
    plt.ylabel('Transfer Cost')
    plt.title('Total transfer cost after Gameweek %i'%nGW)
    plt.savefig('Transfer_Cost_%s.png' %leagueID, bbox_inches='tight')
    plt.close()
    
    ##****************  League Rank ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    i=0
    for key,group in g:
        plt.plot(group['GW'],group['League Rank'],'.-',lw=10,markersize=10,label=key,color=plt.cm.Paired(rgbs[i]))
        i=i+1
    plt.gca().invert_yaxis()
    plt.xlim(0.95,nGW+0.05)
    plt.ylim(len(teamList)+0.5,0.5)
    plt.xticks(range(1,nGW+1))
    plt.yticks(range(1,len(teamList)+1))
    plt.xlabel('Gameweek')
    plt.ylabel('League Rank')
    i=0
    for key,group in g:
        labelText=(key+' ('+str(int(group['Overall Points'].max()))+' points)')
        ax.text(nGW+0.1,i+1,labelText,verticalalignment='center')
        i=i+1
    plt.savefig('League_Rank_%s.png' %leagueID, bbox_inches='tight')
    plt.close()
    
    ##**************** Gameweek Points (scatter per player) ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    plt.hold(True)
    labels=[]
    i=1
    for key,group in g:
        plt.scatter([i]*len(group),group['Gameweek Points'],s=100,marker='*',label=key,color=plt.cm.Paired(rgbs[i-1]))
        labels.append(key)
        i=i+1
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    plt.xticks(range(1,len(teamList)+1), labels, rotation='45',ha='right')
    plt.ylabel('Gamweek Points')
    plt.title('Points per Gameweek')
    plt.savefig('Scatter_Points_%s.png' %leagueID, bbox_inches='tight')
    plt.close()
    
    ##**************** Team Value vs. League Rank (scatter) ***********************************##
    fig,ax=plt.subplots(figsize=(20,10))
    colors = np.random.rand(len(dfp))
    i=0
    for key,r in dfp.iterrows():
        plt.scatter(r['Team Value'],r['League Rank'],s=300,label=key,color=plt.cm.Paired(rgbs[i]))
        ax.text(r['Team Value']+0.12,i+1,key,verticalalignment='center')
        i=i+1
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_axisbelow(True)
    plt.gca().invert_yaxis()
    plt.yticks(range(1,len(teamList)+1))
    plt.xlabel('Team Value')
    plt.ylabel('League Rank')
    plt.title('Team Value vs. League Rank after Gameweek %i' %nGW)
    plt.savefig('Scatter_League_Rank_Team_Value_%s.png' %leagueID, bbox_inches='tight')
