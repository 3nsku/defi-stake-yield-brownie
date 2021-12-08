import { Token } from "../Main"
import {useEthers, useTokenBalance, useNotifications} from '@usedapp/core'
import {formatUnits} from "@ethersproject/units"
import {utils} from "ethers"
import {Input, Button, CircularProgress, Snackbar} from "@material-ui/core"
import Alert from '@material-ui/lab/Alert'
import React, {useEffect, useState} from "react"
import { useStakeTokens } from "../../hooks/useStakeTokens"


export interface StakeFormProps {
    token: Token
}

export const StakeForm = ({token}: StakeFormProps) => {
    const {address: tokenAddress, name} = token
    const {account} = useEthers()
    const tokenBalance = useTokenBalance(tokenAddress, account)
    const fomartedTokenBalance = tokenBalance ? parseFloat(formatUnits(tokenBalance, 18)) : 0
    const { notifications } = useNotifications()
    const [amount, setAmount] = useState<number | string | Array<number | string>>(0)

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const newAmount = event.target.value === "" ? "" : Number (event.target.value)
        setAmount(newAmount)
        console.log(newAmount)
    }

    const {ApproveAndStake:ApproveAndStake, state:approveErc20State} = useStakeTokens(tokenAddress)

    const handleStakeSubmit = () => {

        const amountAsWei = utils.parseEther(amount.toString())
        return ApproveAndStake(amountAsWei.toString())
    }

    const isMining = approveErc20State.status === "Mining"
    const [showErc20ApprovalSuccess, setShowErc20ApprovalSuccess] = useState(false)
    const [showStakeTokenSuccess, setShowStakeTokenSuccess] = useState(false)
    const handleCloseSack = () => {
        setShowStakeTokenSuccess(false)
        setShowErc20ApprovalSuccess(false)
    }

    useEffect(() => {
        if (notifications.filter(
            (notification) => 
                notification.type === "transactionSucceed" && 
                notification.transactionName === "Approve ERC20 Transfer").length > 0) {
                    setShowErc20ApprovalSuccess(true)
                    setShowStakeTokenSuccess(false)
        }
        if (notifications.filter(
            (notification) => 
                notification.type === "transactionSucceed" && 
                notification.transactionName === "Stake Tokens").length > 0) {
                console.log("Tokens Staked!")
                setShowErc20ApprovalSuccess(false)
                setShowStakeTokenSuccess(true)
        }
    }, [notifications, showErc20ApprovalSuccess, showStakeTokenSuccess])

    return (
        <>
        <div>
        <Input onChange={handleInputChange}/>
        <Button onClick={handleStakeSubmit} color="primary" disabled={isMining} size="large">{isMining ? <CircularProgress size={26} /> : "STAKE"}</Button>
        </div>

        <Snackbar 
        open={showErc20ApprovalSuccess} 
        autoHideDuration={5000} 
        onClose={handleCloseSack}>
            <Alert severity="success" onClose={handleCloseSack}> 
                ERC-20 token trasfer approved! Now approve the 2nd transaction!
            </Alert>
        </Snackbar>
        <Snackbar open={showStakeTokenSuccess} autoHideDuration={5000} onClose={handleCloseSack}>
            <Alert onClose={handleCloseSack} severity="success">
                Tokens Staked!
            </Alert>
        </Snackbar>
        </>
    )
}

