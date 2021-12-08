import {makeStyles} from '@material-ui/core'

const useStyles = makeStyles((theme) => ({
    container: {
        display: "inline-grid",
        gripTemplateColumns: "auto auto auto",
        gap: theme.spacing(1),
        alignItems: "center"
    },
    tokenImg: {
        width: "32px",
        margin: "0 auto"
        
    },
    amount: {
        fontWeight: 700,
        display: "flex",
        flexDirection: "row",
        justifyContent: "center"
    }
  }))

interface BalanceMsgProps {
    label: string
    tokenImgSrc: string
    amount: number
}

export const BalanceMsg = ({label, tokenImgSrc, amount}: BalanceMsgProps) => {
    const classes = useStyles()
   
    return (
        <div className={classes.container}>
            <div>{label}</div>
            <div className={classes.amount}>{amount}</div>
            <img className={classes.tokenImg} src={tokenImgSrc} alt="image logo"/>
        </div>
        )
}