import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855-kafka.eastus2.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Energy Usage</th>
							<th>Temperature Change</th>
						</tr>
						<tr>
							<td># E: {stats['num_ec_readings']}</td>
							<td># T: {stats['num_temp_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Energy: {stats['max_ec_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Min Energy: {stats['max_ec_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Temperature: {stats['max_temp_reading']}</td>
						</tr>
                        <tr>
                            <td colspan="2">Min Temperature: {stats['min_temp_reading']}</td>
                        </tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
