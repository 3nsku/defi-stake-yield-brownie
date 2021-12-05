import {useEthers} from '@usedapp/core'
import {Button, makeStyles} from '@material-ui/core'

const useStyles = makeStyles((theme) => ({
    container: {
        padding: theme.spacing(4),
        display: "flex",
        justifyContent: "flex-end",
        gap: theme.spacing(1)
    }
  }))

// this is a typescript way of saying that Header is a function that inside the brackets write what you want it to do.
export const Header = () => {
    const classes = useStyles()
    const { activateBrowserWallet, account, deactivate } = useEthers()

    // check if the user is already connected!
    const isConnected = account !== undefined

    // if connected show disconnect button, is not show connect button
    return (
        <div className={classes.container}>
        <div>
            {isConnected ? (
                <button onClick={deactivate}> Disconnect</button>
            ) : (
                <button onClick={() => activateBrowserWallet()}>Connect</button>
            )
            
            } 
        </div>
        </div>
    )
}