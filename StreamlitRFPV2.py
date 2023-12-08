import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
import io
import pyodbc

st.markdown("[Download RFP TemplateV2.xlsx](https://logrgadmin.sharepoint.com/teams/engineering/Shared%20Documents/General/Job%20Aids/RFPTool/RFPToolV2.xlsx)", unsafe_allow_html=True)
st.markdown("[Download EIA Diesel Price Template.xlsx](https://logrgadmin.sharepoint.com/teams/engineering/Shared%20Documents/General/Job%20Aids/RFPTool/EIA-diesel-US-Price.xlsx)", unsafe_allow_html=True)


st.title("RFPToolV2")

def main_query(start_date, end_date, OrganizationName):
    # Your SQL query with parameters
    query = f"""


SELECT
[loadid] as 'RfpLoadId'
, [CityNameOrig] as'OrigCity', [StateCodeOrig] as 'StateOrig', [PostalCodeOrig] as 'OrigPostal',[CountryIdOrig] as 'OrigCountry',[AddrNameOrig]
, [CityNameDest] as 'DestCity',[StateCodeDest] as 'StateDest',[PostalCodeDest] as 'DestPostal',[CountryIdDest] as 'DestCountry',[AddrNameDest]
, format([DateTime_PlannedStart],'MM/dd/yyyy') as 'ShippedDate',[HandlingUnitCountTot],[PieceCountTot]
, [WtBase_GrossTot] as 'Weight'
,greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth]) as 'Max_dim'
,[50] AS WClass50,[55] AS WClass55,[60] AS WClass60,[65] AS WClass65,[70] AS WClass70,[77.5] AS [WClass77.5],[85] AS WClass85,[92.5] AS [WClass92.5], [100] AS WClass100,[110] AS WClass110,[125] AS WClass125,[150] AS WClass150,[175] AS WClass175,[200] AS WClass200,[250] AS WClass250,[300] AS WClass300,[400] AS WClass400
,CSD,HAZMAT,INSDD,INSDP,LFGP,LFGD,LAP,LAD,NFY,RESP,RESD,TRDSHW,APPT,
case 
	when greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])<8 and greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])>=6 then [EXL]
	else NULL
end as 'EXL6-8',
case 
	when greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])<10 and greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])>=8 then [EXL]
	else NULL
end as 'EXL8-10',
case 
	when greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])<12 and greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])>=10 then [EXL]
	else NULL
end as 'EXL10-12'
,case 
	when greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])<16 and greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])>=12 then [EXL]+[EXL12-16]
	else NULL
end as 'EXL12-16'
,case 
	when greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])<20 and greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])>=16 then [EXL]+[EXL16-20]
	else NULL
end as 'EXL16-20'
,case 
	when greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])<28 and greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])>=20 then [EXL]+[EXL20-28]
	else NULL
end as 'EXL20-28'
,case 
	when greatest([Dim_HandlingUnitHeight],[Dim_HandlingUnitLength],[Dim_HandlingUnitWidth])>28 then [EXL]
	else NULL
end as 'EXL>28'

,[Fuel Surcharge] as 'Fuel_history', CurrencyBase_NetFreightCostTot as 'Linehaul_history'
, COALESCE(CSD,0)+COALESCE(HAZMAT,0)+COALESCE(INSDD,0)+COALESCE(INSDP,0)+COALESCE(LFGP,0)+COALESCE(LFGD,0)+COALESCE(LAP,0)+COALESCE(LAD,0)+COALESCE(NFY,0)+COALESCE(RESP,0)+COALESCE(RESD,0)+COALESCE(TRDSHW,0)+COALESCE(APPT,0)
+COALESCE([EXL12-16],0)+COALESCE([EXL16-20],0)+COALESCE([EXL20-28],0)+COALESCE([EXL],0)

as 'Accesorial Total_history'
, (isnull(COALESCE(CSD,0)+COALESCE(HAZMAT,0)+COALESCE(INSDD,0)+COALESCE(INSDP,0)+COALESCE(LFGP,0)+COALESCE(LFGD,0)+COALESCE(LAP,0)+COALESCE(LAD,0)+COALESCE(NFY,0)+COALESCE(RESP,0)+COALESCE(RESD,0)+COALESCE(TRDSHW,0)+COALESCE(APPT,0)
+COALESCE([EXL12-16],0)+COALESCE([EXL16-20],0)+COALESCE([EXL20-28],0)+COALESCE([EXL],0),0)+COALESCE([Fuel Surcharge],0)+CurrencyBase_NetFreightCostTot) as'Total'
FROM (
  SELECT ordload.[loadid], [DateTime_PlannedStart], ordload.[CityNameOrig], ordload.[StateCodeOrig], ordload.[PostalCodeOrig], ordload.[CountryIdOrig],ordload.[CityNameDest],ordload.[StateCodeDest],ordload.[PostalCodeDest],ordload.[CountryIdDest]
  , [WtBase_GrossTot],ordload.[HandlingUnitCountTot],ordload.[PieceCountTot]
  ,(select top 1 Dim_HandlingUnitHeight*0.0833
  from [3gOrderLine] as ordline
  join [3gLoad_ord] as a on a.OrdHeaderId = ordline.OrdHeaderId
  where ordload.loadId = a.loadId
  order by Dim_HandlingUnitHeight DESC) as 'Dim_HandlingUnitHeight'
  , (select top 1 Dim_HandlingUnitLength*0.0833
  from [3gOrderLine] as ordline
  join [3gLoad_ord] as a on a.OrdHeaderId = ordline.OrdHeaderId
  where ordload.loadId = a.loadId
  order by Dim_HandlingUnitLength DESC) as 'Dim_HandlingUnitLength'
  , (select top 1 Dim_HandlingUnitWidth*0.0833
  from [3gOrderLine] as ordline
  join [3gLoad_ord] as a on a.OrdHeaderId = ordline.OrdHeaderId
  where ordload.loadId = a.loadId
  order by Dim_HandlingUnitWidth DESC) as 'Dim_HandlingUnitWidth'
  ,[AddrNameOrig],[AddrNameDest]
  , lodline.[DataValue_FreightClass], [WtBase_Gross], ordload.[DistBase_Tot]
  , ordload.CurrencyBase_NetFreightCostTot, ordload.CurrencyBase_NetAccessorialCostTot, ordload.CurrencyAmt_NetCostTot
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'FSC','295','BSC','ENC','FUL')
)		as [Fuel Surcharge]
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'CSD')
)		as CSD
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'HAZMAT','HAZM','HIC','HZ1','HZ2','HZ3','HMI','310','420','425','645','DGS','EPS')
)		as HAZMAT
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'HFA','IDL','INSDD','SEF')
)		as INSDD
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'IDU','INSDP','IPU')
)		as INSDP
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'LFGP','LG2')
)		as LFGP
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'LFGD','LG1')
)		as LFGD
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'LAP')
)		as LAP
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'LAD','ACH')
)		as LAD
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'ACC','MNC','NCH','NFY','NFYD','NFYP','NTFYAPPTD')
)		as NFY
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'PRU','RESP')
)		as RESP
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'PRD','RES','RESD')
)		as RESD
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'TRDSHW','EBD','EBP')
)		as TRDSHW
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'APPT','APTP','ARR','GHT','GMS1','GMS2''GMS3''GMS4')
)		as APPT
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'EXL','520','BKA')
)		as 'EXL'
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'EXL2')
)		as 'EXL12-16'
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'EXL3')
)		as 'EXL16-20'
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'EXL4')
)		as 'EXL20-28'
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'DEP','DET','DET1','DET2','DET3','DET4','DET5','DET6','DET7','DET8','DETEN','DEW','DPU','DRV','DTL','DTV','DWP','SBC','TDD','TDO','TDQ','TDT','WTM')
)		as DET
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( '145','BCF','CBF','OSC','CBC','CNSO','CCC')
)		as CBF
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'CCH','INSP','SCL','SCU','WRE')
)		as INSP
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'BLC','BOLC','LAC')
)		as BOLC
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'CALC','CAS','CCS')
)		as CCS
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'DIC','RAA','RCC','RCD','RDC')
)		as RCC
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'REW','REWGH')
)		as REWGH
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'SINGLE','SSF','SSM')
)		as SINGLE
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'SEG','STSG')
)		as SEG
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode NOT in( 'SEG','STSG','SINGLE','SSF','SSM','CALC','CAS','CCS','REW','REWGH''DIC','RAA','RCC','RCD','RDC','BLC','BOLC','LAC','CCH','INSP','SCL','SCU','WRE', 'HAZMAT','HAZM','HIC','HZ1','HZ2','HZ3','HMI','310','420','425','645','DGS','EPS','APPT','APTP','ARR','GHT','GMS1','GMS2''GMS3''GMS4','145','BCF','CBF','OSC','CBC','CNSO','CCC','DEP','DET','DET1','DET2','DET3','DET4','DET5','DET6','DET7','DET8','DETEN','DEW','DPU','DRV','DTL','DTV','DWP','SBC','TDD','TDO','TDQ','TDT','WTM','EXL4','EXL3','EXL2','EXL','520','BKA','TRDSHW','EBD','EBP', 'PRD','RES','RESD','PRU','RESP','ACC','MNC','NCH','NFY','NFYD','NFYP','NTFYAPPTD','LAD','ACH','LAP','LFGD','LG1','LFGP','LG2','IDU','INSDP','IPU','HFA','IDL','INSDD','SEF','CSD', 'FSC','295','BSC','ENC','FUL')
)		as MISC
 FROM [dbo].[3gLoad] as ordload
 INNER JOIN [dbo].[3gLoadLine] as lodline ON lodline.LoadId = ordload.LoadId
 left join [3gOrganization] org on ordload.organizationid = org.OrganizationId
 WHERE org.OrganizationName = '{OrganizationName}' AND ordload.DateTime_PlannedStart >= '{start_date}' AND ordload.DateTime_PlannedStart <= '{end_date}' 
  and ordload.DataValue_LoadTmsStatus in ('Closed','Complete','Delivered') and ordload.TransportModeName in ('LTL')
) AS ClassData

PIVOT
(
   SUM(WtBase_Gross)
  FOR [DataValue_FreightClass] IN ([50],[55],[60],[65],[70],[77.5],[85],[92.5],[100],[110],[125],[150],[175],[200],[250],[300],[400])
) AS pivot_table
order by loadid



"""

    return query

def other_query(start_date, end_date, OrganizationName):
    # Your SQL query with parameters
    query = f"""

SELECT
[loadid] as 'RfpLoadId', sum(DET) DET,sum(CBF) CBF,sum(INSP) INSP,sum(BOLC) BOLC,sum(CCS) CCS
,sum(RCC) RCC,sum(REWGH) REWGH,sum(SINGLE) SINGLE,sum(SEG) SEG,sum(MISC) MISC
FROM (
  SELECT ordload.[loadid], [DateTime_PlannedStart], ordload.[CityNameOrig], ordload.[StateCodeOrig], ordload.[PostalCodeOrig], ordload.[CountryIdOrig],ordload.[CityNameDest],ordload.[StateCodeDest],ordload.[PostalCodeDest],ordload.[CountryIdDest]
  , [WtBase_GrossTot],ordload.[HandlingUnitCountTot],ordload.[PieceCountTot]
  ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'DEP','DET','DET1','DET2','DET3','DET4','DET5','DET6','DET7','DET8','DETEN','DEW','DPU','DRV','DTL','DTV','DWP','SBC','TDD','TDO','TDQ','TDT','WTM')
)		as DET
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( '145','BCF','CBF','OSC','CBC','CNSO','CCC')
)		as CBF
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'CCH','INSP','SCL','SCU','WRE')
)		as INSP
 ,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'BLC','BOLC','LAC')
)		as BOLC
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'CALC','CAS','CCS')
)		as CCS
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'DIC','RAA','RCC','RCD','RDC')
)		as RCC
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'REW','REWGH')
)		as REWGH
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'SINGLE','SSF','SSM')
)		as SINGLE
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode in( 'SEG','STSG')
)		as SEG
,(
	select sum(chr.CurrencyAmt_NetCharge)
	from [3gOrdCharge] chr
	join [3gAccessorialCode] acc on acc.AccessorialCodeId = chr.AccessorialCodeId
	join [3gLoad_Ord] ordlod on chr.OrdHeaderid = ordlod.OrdHeaderId
	where ordlod.LoadId = ordload.LoadId
	and acc.AccCode NOT in( 'SEG','STSG','SINGLE','SSF','SSM','CALC','CAS','CCS','REW','REWGH''DIC','RAA','RCC','RCD','RDC','BLC','BOLC','LAC','CCH','INSP','SCL','SCU','WRE', 'HAZMAT','HAZM','HIC','HZ1','HZ2','HZ3','HMI','310','420','425','645','DGS','EPS','APPT','APTP','ARR','GHT','GMS1','GMS2''GMS3''GMS4','145','BCF','CBF','OSC','CBC','CNSO','CCC','DEP','DET','DET1','DET2','DET3','DET4','DET5','DET6','DET7','DET8','DETEN','DEW','DPU','DRV','DTL','DTV','DWP','SBC','TDD','TDO','TDQ','TDT','WTM','EXL4','EXL3','EXL2','EXL','520','BKA','TRDSHW','EBD','EBP', 'PRD','RES','RESD','PRU','RESP','ACC','MNC','NCH','NFY','NFYD','NFYP','NTFYAPPTD','LAD','ACH','LAP','LFGD','LG1','LFGP','LG2','IDU','INSDP','IPU','HFA','IDL','INSDD','SEF','CSD', 'FSC','295','BSC','ENC','FUL')
)		as MISC
 FROM [dbo].[3gLoad] as ordload
 INNER JOIN [dbo].[3gLoadLine] as lodline ON lodline.LoadId = ordload.LoadId
 left join [3gOrganization] org on ordload.organizationid = org.OrganizationId
 WHERE org.OrganizationName = '{OrganizationName}' AND ordload.DateTime_PlannedStart >= '{start_date}' AND ordload.DateTime_PlannedStart <= '{end_date}' 
  and ordload.DataValue_LoadTmsStatus in ('Closed','Complete','Delivered') and ordload.TransportModeName in ('LTL')
) AS ClassData
group by LoadId



 """
    return query

def create_excel_file(query_data,other_data):
    sheet_RFP_Loads = pd.DataFrame(query_data)
    sheet_Other_Accessorials = pd.DataFrame(other_data)
    df_RfpCarrier = {'RfpCarrierId':[], 'CarrierCode':[], 'Carrier Name':[],'IsIncumbent':[],'BaseRateId':[],'DiscMinTableId':[],'ServiceRateId':[],'FuelTableId':[],'AccessorialTableId':[]} 
    sheet_RfpCarrier = pd.DataFrame(df_RfpCarrier)
    df_AccessirialDataBase = {'AccessorialTableId':[],'AccessorialCode':[],'Min':[],'Max':[],'Cwt':[]} 
    sheet_AccessirialDataBase = pd.DataFrame(df_AccessirialDataBase)
    df_RfpServiceRates = {'ServiceRateId':[],'ServiceRateName':[],'ContractId':[],'ContractStatus':[],'TPNumber':[]} 
    sheet_RfpServiceRates = pd.DataFrame(df_RfpServiceRates)
    df_RfPBaseRates = {'BaseRateId':[],'BaseRateName':[],'ContractId':[],'ContractStatus':[],'TPNumber':[]} 
    sheet_RfPBaseRates = pd.DataFrame(df_RfPBaseRates)
    df_RfpFuelTable = {'FuelTableId':[],'FuelTableName':[]} 
    sheet_RfpFuelTable = pd.DataFrame(df_RfpFuelTable)
    df_FuelTables = {'FuelTableValueId':[],'FuelTableId':[],'USDieselValueMin':[],'USDieselValueMax':[],'FuelSurcharge%':[]} 
    sheet_FuelTables = pd.DataFrame(df_FuelTables)
    df_BaseRate = {'RfpLoadId':[],'BaseRateId':[],'BaseRateAmount':[]} 
    sheet_BaseRate = pd.DataFrame(df_BaseRate)
    df_DiscountMinDatabase = {'Carrier':[],'StateOrig':[],'OrigPostal':[],'StateDest':[],'DestPost':[],'Disc':[],'Min':[]} 
    sheet_DiscountMinDatabase = pd.DataFrame(df_DiscountMinDatabase)
    df_RfpServiceTable = {'RfpServiceId':[],'RfpLoadId':[],'ServiceRateId':[],'ServiceDays':[]} 
    sheet_RfpServiceTable = pd.DataFrame(df_RfpServiceTable)
    output_template = io.BytesIO()
    with pd.ExcelWriter(output_template, engine='xlsxwriter') as writer:
        sheet_RFP_Loads.to_excel(writer, sheet_name='RFP_Loads', index=False)
        sheet_Other_Accessorials.to_excel(writer, sheet_name='Other_Accessorials', index=False)
        sheet_RfpCarrier.to_excel(writer, sheet_name='RfpCarrier', index=False)
        sheet_AccessirialDataBase.to_excel(writer, sheet_name='AccessirialDataBase', index=False)
        sheet_RfpServiceRates.to_excel(writer, sheet_name='RfpServiceRates', index=False)
        sheet_RfPBaseRates.to_excel(writer, sheet_name='RfPBaseRates', index=False)
        sheet_RfpFuelTable.to_excel(writer, sheet_name='RfpFuelTable', index=False)
        sheet_FuelTables.to_excel(writer, sheet_name='FuelTables', index=False)
        sheet_BaseRate.to_excel(writer, sheet_name='BaseRate', index=False)
        sheet_DiscountMinDatabase.to_excel(writer, sheet_name='DiscountMinDatabase', index=False)
        sheet_RfpServiceTable.to_excel(writer, sheet_name='RfpServiceTable', index=False)
    
    excel_data_template = output_template.getvalue()
    return excel_data_template

def unique(list1):
    ans = pd.Series(list1).drop_duplicates().to_list()
    return ans

def find_closest_fuel_tier(diesel_tier,value):
    value = float(value)
    result = min(diesel_tier,key = lambda x: max(0,value-x))
    return result

def Filter(df,selected,col_name):
    result = df[df[col_name].isin(selected)]
    return result

def multiselect_with_select_all(label, options):
    # Create a multiselect widget with "Select All" option
    selected_options = st.sidebar.multiselect(label, ["Select All"] + options,default=["Select All"])

    # Check if "Select All" is selected and update the selected_options accordingly
    if "Select All" in selected_options:
        selected_options = options
    return selected_options

def AwardTable(SelectQueryMetric,time_span):
    temp_df = merged_df_shipment.copy()
    if SelectQueryMetric == "Lowest Cost":
        temp_df = Filter(temp_df,[1],'RankTotalRate')
    elif SelectQueryMetric == "2nd Lowest Cost":
        temp_df = Filter(temp_df,[2],'RankTotalRate')
    elif SelectQueryMetric == "3rd Lowest Cost":
        temp_df = Filter(temp_df,[3],'RankTotalRate')
    else:
        temp_df = Filter(temp_df,[1],'RankServiceDays')
    df_award = temp_df.groupby('CarrierCode').agg({"TotalRate":'sum','ServiceDays':'mean','RfpLoadId':'count','Weight_x':'sum'})
    df_award['Annualized Awarded Revenue($)']=df_award['TotalRate']*365/time_span
    df_award['Annualized Awarded #Shipment']=round(df_award['RfpLoadId']*365/time_span,0)
    df_award['Annualized Awarded Weight(lbs)']=df_award['Weight_x']*365/time_span
    df_award=df_award.round(2)
    df_award=df_award.reset_index()
    df_award.columns=df_award.columns.str.replace('RfpLoadId',"#Shipment")
    df_award.columns=df_award.columns.str.replace('Weight_x',"Weight(lbs)")
    df_award.columns=df_award.columns.str.replace('TotalRate',"Total Awarded Revenue($)")
    df_award.columns=df_award.columns.str.replace('ServiceDay',"Average Service Day")
    return df_award


def Bid_price(SelectQueryMetric,time_span):
    Historic_Total = df_loads['Total Charge_history'].sum().round(2)
    Annualized_historic_total = (Historic_Total*365/time_span).round(2)
    temp_df = merged_df_shipment.copy()
    if SelectQueryMetric == "Lowest Cost":
        temp_df = Filter(temp_df,[1],'RankTotalRate')
    elif SelectQueryMetric == "2nd Lowest Cost":
        temp_df = Filter(temp_df,[2],'RankTotalRate')
    elif SelectQueryMetric == "3rd Lowest Cost":
        temp_df = Filter(temp_df,[3],'RankTotalRate')
    else:
        temp_df = Filter(temp_df,[1],'RankServiceDays')
    Bid_total = temp_df['TotalRate'].sum().round(2)
    Annualized_bid = (Bid_total*365/time_span).round(2)
    saving_bid = Historic_Total-Bid_total.round(2)
    Annualized_saving = (Annualized_historic_total-Annualized_bid).round(2)
    saving_percent = (saving_bid/Historic_Total*100).round(2)
    Total_data = {'Group': ['Total($)', 'Annualized Total($)','Saving($)', 'Annualized Savings($)','Savings(%)'],
                'Historic Pricing': [Historic_Total,Annualized_historic_total,'' ,'' ,'' ],
                'Bid Pricing':[Bid_total,Annualized_bid,saving_bid,Annualized_saving,saving_percent]}
    Total_table = pd.DataFrame(Total_data).T
    Total_table.columns=Total_table.iloc[0]
    Total_table=Total_table[1:]
    return Total_table

def bid_analysis(SelectQueryMetric):
    temp_df = merged_df_shipment
    if SelectQueryMetric == "Lowest Cost":
        temp_df = Filter(temp_df,[1],'RankTotalRate')
    elif SelectQueryMetric == "2nd Lowest Cost":
        temp_df = Filter(temp_df,[2],'RankTotalRate')
    elif SelectQueryMetric == "3rd Lowest Cost":
        temp_df = Filter(temp_df,[3],'RankTotalRate')
    else:
        temp_df = Filter(temp_df,[1],'RankServiceDays')
    selected_column = ['RfpLoadId','OrigCity', 'StateOrig', 'OrigPostal_x', 'OrigCountry','DestCity', 'StateDest', 'DestPostal', 'DestCountry','BaseRateAmount','CarrierCode','Disc', 'Min','Fuel','Linehaul','Access_Total','TotalRate','Linehaul_history', 'Fuel_history','ServiceDays',]
    result = temp_df[selected_column]
    result = result.merge(new_acc, on = ['RfpLoadId','CarrierCode'])
    result = result.rename(columns={'OrigPostal_x':'OrigPostal','BaseRateAmount':'Czar','Access_Total':'Accessorials'})
    return result


def convert_df_T(df):
   return df.to_csv(index=True).encode('utf-8')

def convert_df_F(df):
   return df.to_csv(index=False).encode('utf-8')

def accessorial_summary(SelectQueryMetric):
    temp_df = merged_df_shipment
    if SelectQueryMetric == "Lowest Cost":
        temp_df = Filter(temp_df,[1],'RankTotalRate')
    elif SelectQueryMetric == "2nd Lowest Cost":
        temp_df = Filter(temp_df,[2],'RankTotalRate')
    elif SelectQueryMetric == "3rd Lowest Cost":
        temp_df = Filter(temp_df,[3],'RankTotalRate')
    else:
        temp_df = Filter(temp_df,[1],'RankServiceDays')
    pivot_acc_sum = pd.pivot_table(temp_df, values=AccessorialCode_y, index='CarrierCode', aggfunc={acc: 'sum' for acc in AccessorialCode_y}, fill_value=0)
    pivot_acc_sum=pd.DataFrame(pivot_acc_sum).T
    pivot_acc_sum=pivot_acc_sum.rename(index=lambda x:x.replace('_y',''))
    pivot_acc_cnt = pd.pivot_table(temp_df, values=AccessorialCode_y, index='CarrierCode', aggfunc={acc: lambda x: (x != 0).sum() for acc in AccessorialCode_y}, fill_value=0)
    pivot_acc_cnt=pd.DataFrame(pivot_acc_cnt).T
    pivot_acc_cnt=pivot_acc_cnt.rename(index=lambda x:x.replace('_y',''))
    hist_acc = pd.DataFrame({
        'Historical Total Accessorial': temp_df[AccessorialCode_x].sum(),
        'Historical Accessorial Count': (temp_df[AccessorialCode_x]).count()
    })
    hist_acc = hist_acc.rename(index=lambda x:x.replace('_x',''))
    result = pd.merge(pivot_acc_cnt, pivot_acc_sum, left_index=True, right_index=True, suffixes=('_cnt', '_sum'))
    
    for accessorial in result.columns:
        if accessorial.endswith('_sum'):
            cnt_column = accessorial.replace('_sum', '_cnt')
            average_column = accessorial.replace('_sum', '_avg')
            result[average_column] = result[accessorial] / result[cnt_column]
    result = result[sorted(result.columns)]
    result = pd.merge(hist_acc, result, left_index=True, right_index=True, suffixes=('_historical', ''))
    sum_columns = result.filter(like='_sum', axis=1)
    result['Solution_sum']=sum_columns.sum(axis=1)
    result['Accessorial Saving%']=round((result['Historical Total Accessorial']-result['Solution_sum'])*100/result['Historical Total Accessorial'],2)
    return result

def accessorial_summary_bylane(SelectQueryMetric):
    temp_df = merged_df_shipment
    if SelectQueryMetric == "Lowest Cost":
        temp_df = Filter(temp_df,[1],'RankTotalRate')
    elif SelectQueryMetric == "2nd Lowest Cost":
        temp_df = Filter(temp_df,[2],'RankTotalRate')
    elif SelectQueryMetric == "3rd Lowest Cost":
        temp_df = Filter(temp_df,[3],'RankTotalRate')
    else:
        temp_df = Filter(temp_df,[1],'RankServiceDays')
    temp_df['lane']=temp_df['StateOrig']+'-'+temp_df['StateDest']
    temp_df.columns = [col.replace('_y','') for col in temp_df.columns]

    result = temp_df.groupby('lane')[AccessorialCode].agg(['sum', lambda x: (x != 0).sum()])
    result = result.rename(columns={'<lambda_0>': 'count'})

    return result

st.header('RfpLoad Query Generator')

# __SERVER__=st.secrets["SERVER"]
# __DATABASE__=st.secrets["DATABASE"]
# __DRIVER__=st.secrets["DRIVER"]
# __USER__=st.secrets["USER"]
# __PASS__=st.secrets["PASS"]
# connection_string="DRIVER="+__DRIVER__+';SERVER='+__SERVER__+';PORT=1443;DATABASE='+__DATABASE__+';AUTHENTICATION=ActiveDirectoryPassword'+';Encrypt=yes'+';UID='+__USER__+';PWD='+__PASS__
# connection = pyodbc.connect(connection_string)

@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["SERVER"]
        + ";DATABASE="
        + st.secrets["DATABASE"]
        + ";UID="
        + st.secrets["USER"]
        + ";PWD="
        + st.secrets["PASS"]
    )

conn = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


start_date = st.date_input('Start Date', value=None)
end_date = st.date_input('End Date', value=None)
OrganizationName = st.text_input('Organization Name',value = "")

query1 = main_query('2023-05-01','2023-06-01',OrganizationName)
# df_main_query = pd.read_sql(query1, connection)
df_main_query = run_query(query1)

query2 = other_query('2023-05-01','2023-06-01',OrganizationName)
# df_other_query = pd.read_sql(query2,connection)
df_other_query = run_query(query2)


st.download_button(label="Download RFP Template", data=create_excel_file(df_main_query,df_other_query), file_name="RFP_Template.xlsx", key='download')


st.header('File Input')
input_file1 = st.file_uploader("Upload the RFP Excel Template", type=["xls", "xlsx"])
input_file2 = st.file_uploader("Upload the EIA Diesel Price Sheet ", type=["xls", "xlsx"])

if input_file1 is not None and input_file2 is not None:
    df_loads = pd.read_excel(input_file1 ,sheet_name='RFP-Loads')
    df_loads['ShippedDate']=pd.to_datetime(df_loads['ShippedDate'])
    df_loads['WeekNum']=df_loads['ShippedDate'].dt.isocalendar().week
    df_loads['Year'] = df_loads['ShippedDate'].dt.isocalendar().year
    df_USDiesel = pd.read_excel(input_file2)
    df_carrier = pd.read_excel(input_file1 ,sheet_name='RfpCarrier')
    df_dis = pd.read_excel(input_file1 ,sheet_name='DiscountMinDatabase')
    df_base = pd.read_excel(input_file1,sheet_name='BaseRate')
    df_service = pd.read_excel(input_file1,sheet_name='RfpServiceTable')
    df_fuel = pd.read_excel(input_file1, sheet_name='FuelTables')
    df_access = pd.read_excel(input_file1,sheet_name='AccessorialDataBase')
    df_access['Acc_identifier']=df_access['AccessorialTableId'].astype(str)+'-'+df_access['AccessorialCode']
    diesel_tier = list(df_fuel['USDieselValueMax'])

    carrier_list = list(df_carrier['CarrierCode'])
    
    #selection bar layout

    #incumbent Filter
    incumbent_option = st.sidebar.radio("Incumbent:",['all carriers','only incumbent'])
    incum_carrier = list(df_carrier[df_carrier['IsIncumbent']==1]['CarrierCode'])
    if incumbent_option =="only incumbent":
        df_carrier = Filter(df_carrier,incum_carrier,'CarrierCode')
        carrier_ava = incum_carrier
    elif incumbent_option=="all carriers":
        carrier_ava=carrier_list

    #Carrier Selection Filter
    selected_carrier = multiselect_with_select_all("Select Carrier(s)",carrier_ava)
    df_carrier = Filter(df_carrier,selected_carrier,'CarrierCode')

    #Origin Selection Filter
    OrigList = unique(df_loads["StateOrig"])
    selected_orig = multiselect_with_select_all("Select Origin(s)",OrigList)
    df_loads = Filter(df_loads,selected_orig,'StateOrig')

    #Dest Selection Filter
    DestList = unique(df_loads["StateDest"])
    selected_dest = multiselect_with_select_all("Select Destination(s)",DestList)
    df_loads = Filter(df_loads,selected_dest,'StateDest')

    #Location Selection Filter
    location_list = list(df_loads['Location'])
    selected_loc = multiselect_with_select_all("Select Location(s)",location_list)
    df_loads = Filter(df_loads,selected_loc,'Location')

    #Query Metric Selection Filter
    QueryMetricList = ["Lowest Cost","2nd Lowest Cost","3rd Lowest Cost","Fastest Transit"]
    SelectQueryMetric = st.sidebar.selectbox("Select Query Metric",QueryMetricList)

    

    fuel_table = df_loads[['Year','WeekNum','RfpLoadId']].merge(df_USDiesel,on=['Year','WeekNum'])
    USDieselValueMax =[]
    for index,shipment in fuel_table.iterrows():
        tier = ''
        value = shipment['Value']
        tier = find_closest_fuel_tier(diesel_tier,value)
        USDieselValueMax.append(tier)
    fuel_table['USDieselValueMax']=USDieselValueMax
    fuel_table = fuel_table.merge(df_fuel,on ='USDieselValueMax')

    merged_df_shipment = df_loads.merge(df_dis,on = ['StateOrig','StateDest'])
    merged_df_shipment = pd.merge(merged_df_shipment,df_carrier,left_on='Carrier',right_on='DiscMinTableId',how = 'inner')
    merged_df_shipment = merged_df_shipment.merge(df_base, on = ['RfpLoadId','BaseRateId'])
    merged_df_shipment['Linehaul']=np.maximum(merged_df_shipment['BaseRateAmount']*(1-merged_df_shipment['Disc']),merged_df_shipment['Min'])
    minfilter = (merged_df_shipment['Linehaul']==merged_df_shipment['Min'])
    merged_df_shipment['IsMin']=np.where(minfilter,'1','0')

    accessorial_col = ['RfpLoadId','CarrierCode','AccessorialTableId','Weight','CSD','HAZMAT','INSDD','INSDP','LFGP','LFGD','LAP','LAD','NFY','RESP','RESD','TRDSHW','APPT','EXL6-8','EXL8-10','EXL10-12','EXL12-16','EXL16-20','EXL20-28','EXL>28']
    AccessorialCode = ['CSD','HAZMAT','INSDD','INSDP','LFGP','LFGD','LAP','LAD','NFY','RESP','RESD','TRDSHW','APPT','EXL6-8','EXL8-10','EXL10-12','EXL12-16','EXL16-20','EXL20-28','EXL>28']
    exist_acc = merged_df_shipment[accessorial_col]

    new_acc = exist_acc.copy()
    for column in AccessorialCode:
        
        for i in range(len(new_acc.index)):
            target_identifier = new_acc.loc[i,'AccessorialTableId'].astype(str)+'-'+column
            minvalue = df_access.loc[df_access['Acc_identifier']==target_identifier,'Min'].values
            maxvalue = df_access.loc[df_access['Acc_identifier']==target_identifier,'Max'].values
            cwtvalue = df_access.loc[df_access['Acc_identifier']==target_identifier,'Cwt'].values

            if pd.isna(new_acc.loc[i,column]):
                weight_temp = 0*new_acc.loc[i,'Weight']
                calc = 0
            else:
                weight_temp = 1*new_acc.loc[i,'Weight']
                calc = weight_temp*cwtvalue/100
                calc = max(minvalue,calc)
                calc = min(maxvalue,calc)
            new_acc.loc[i,column]=calc
    new_acc['Access_Total']=new_acc[AccessorialCode].sum(axis =1)

    merged_df_shipment =merged_df_shipment.merge(new_acc, on = ['RfpLoadId','CarrierCode','AccessorialTableId'])
    merged_df_shipment = merged_df_shipment.merge(df_service,on = ['RfpLoadId','ServiceRateId'])
    merged_df_shipment = merged_df_shipment.merge(fuel_table,on=['RfpLoadId','FuelTableId'])
    merged_df_shipment['Fuel']= merged_df_shipment['Linehaul']*merged_df_shipment['FuelSurcharge%']
    merged_df_shipment['TotalRate']=merged_df_shipment['Linehaul']+merged_df_shipment['Fuel']+merged_df_shipment['Access_Total']
    merged_df_shipment['RankTotalRate']= merged_df_shipment.groupby('RfpLoadId')['TotalRate'].rank(method = 'first')
    merged_df_shipment['RankLinehaul']= merged_df_shipment.groupby('RfpLoadId')['Linehaul'].rank(method = 'first')
    merged_df_shipment['RankLinehaul']= merged_df_shipment.groupby('RfpLoadId')['Linehaul'].rank(method = 'first')
    merged_df_shipment['RankServiceDays']= merged_df_shipment.groupby('RfpLoadId')['ServiceDays'].rank(method = 'first')
    selected_col = ['RfpLoadId','Linehaul','Fuel','Access_Total','CarrierCode','Disc','Min','IsMin','TotalRate','ServiceDays','RankTotalRate','RankLinehaul','RankServiceDays']
    df = merged_df_shipment[selected_col]

    AccessorialCode_y =[ 'CSD_y', 'HAZMAT_y',
       'INSDD_y', 'INSDP_y', 'LFGP_y', 'LFGD_y', 'LAP_y', 'LAD_y', 'NFY_y',
       'RESP_y', 'RESD_y', 'TRDSHW_y', 'APPT_y', 'EXL6-8_y', 'EXL8-10_y',
       'EXL10-12_y', 'EXL12-16_y', 'EXL16-20_y', 'EXL20-28_y', 'EXL>28_y']
    AccessorialCode_x = ['CSD_x', 'HAZMAT_x', 'INSDD_x', 'INSDP_x',
        'LFGP_x', 'LFGD_x', 'LAP_x', 'LAD_x', 'NFY_x', 'RESP_x', 'RESD_x',
        'TRDSHW_x', 'APPT_x', 'EXL6-8_x', 'EXL8-10_x', 'EXL10-12_x',
        'EXL12-16_x', 'EXL16-20_x', 'EXL20-28_x', 'EXL>28_x']

    df_overview = merged_df_shipment.groupby("CarrierCode")['RankTotalRate'].value_counts().unstack(fill_value=0)
    df_fastest = merged_df_shipment.groupby("CarrierCode")['RankServiceDays'].value_counts().unstack(fill_value=0)
    df_fastest = df_fastest[df_fastest.columns[:1]]
    list_top3 = df_overview.columns[:3]
    df_overview = df_overview[list_top3]
    df_overview = df_overview.merge(df_fastest,on="CarrierCode")
    
    df_overview.reset_index(inplace=True)
    
    df_overview=pd.merge(df_overview,df_carrier[['CarrierCode','IsIncumbent']],on = 'CarrierCode')
    df_overview.rename(columns={'CarrierCode': 'CarrierCode', '1.0_x': 'Lowest Cost', 2.0: '2nd Lowest Cost', 3.0: '3rd Lowest Cost', '1.0_y': 'Fastest Transit','Total':'Total'}, inplace=True)
    
    #Annualization Table
    time_span = (df_loads['ShippedDate'].max()-df_loads['ShippedDate'].min()).days

    # incumbent percentage Table
    lowest_cost = merged_df_shipment[merged_df_shipment['RankTotalRate']==1]
    sec_lowest_cost = merged_df_shipment[merged_df_shipment['RankTotalRate']==2]
    third_lowest_cost = merged_df_shipment[merged_df_shipment['RankTotalRate']==3]
    fastest_transit = merged_df_shipment[merged_df_shipment['RankServiceDays']==1]

    p_lowest_cost = round((lowest_cost['IsIncumbent'].sum()/len(lowest_cost)),2)
    p_sec_lowest_cost = round((sec_lowest_cost['IsIncumbent'].sum()/len(sec_lowest_cost)),2)
    p_third_lowest_cost = round((third_lowest_cost['IsIncumbent'].sum()/len(third_lowest_cost)),2)
    p_fastest_transit = round((fastest_transit['IsIncumbent'].sum()/len(fastest_transit)),2)

    Incumb_data = {'Group': ['Lowest Cost', '2nd Lowest Cost','3rd Lowest Cost', 'Fastest Transit'],
                    'Percentage of Incumbency': [p_lowest_cost,p_sec_lowest_cost, p_third_lowest_cost, p_fastest_transit]}
    
    incumbent_table = pd.DataFrame(Incumb_data).T
    incumbent_table.columns=incumbent_table.iloc[0]
    incumbent_table=incumbent_table[1:]

    df_award = AwardTable(SelectQueryMetric,time_span)
    df_total = Bid_price(SelectQueryMetric,time_span)
    df_acc_tbl = accessorial_summary(SelectQueryMetric)
    df_acc_lane = accessorial_summary_bylane(SelectQueryMetric)

    #download 
    csv=convert_df_F(bid_analysis(SelectQueryMetric))
    st.sidebar.download_button(
        label="Download bid analysis",
        data=csv,
        file_name='bid analysis.csv',
        mime='text/csv',
    )

    #download acc summary
    output_acc = io.BytesIO()
    with pd.ExcelWriter(output_acc, engine='xlsxwriter') as writer:
        df_acc_tbl.to_excel(writer, sheet_name='Accessorial Summary Table',index = True)
        df_acc_lane.to_excel(writer, sheet_name='Accessorial Summary By Lane', index=True)

    # Prepare the Excel file for download
    excel_data_acc = output_acc.getvalue()

    # Offer the download of the Excel file
    st.sidebar.download_button(label="Download accessorial summary", data=excel_data_acc, file_name="Accessorial Summary.xlsx", key='download')

    # colt1,colt2 = st.columns(2)
    # with colt1:
    st.subheader('Saving Summary Table')
    st.dataframe(df_total)
    st.subheader('Incumbency Table')
    st.dataframe(incumbent_table)
    st.subheader('Award by Carrier')
    st.dataframe(df_award)
    
    # with colt2:    
    # st.dataframe(df)
    st.subheader('Carrier Summary Table')
    st.dataframe(df_overview)
    


