import {useEthers} from '@usedapp/core'
import {Button, makeStyles} from '@material-ui/core'
import helperConfig from "../helper-config.json"
import networkMapping from "../chain_info/deployments/map.json"
import {constants} from "ethers"
import brownieConfig from "../brownie-config.json"
import dappImg from "../img/dapp.png"
import daiImg from "../img/dai.png"
import ethImg from "../img/eth.png"
import { YourWallet } from './your_wallet'

const useStyles = makeStyles((theme) => ({
    title: {
        color: theme.palette.common.white,
        textAlign: "center",
        padding: theme.spacing(4)
    }
  }))

export type Token = {
    image: string,
    address: string,
    name: string
}

export const Main = () => { 

    const classes = useStyles()

    //get chain id that we are working with
    const { chainId, error } = useEthers()
    const networkName = chainId ? helperConfig[chainId] : "dev"
    //console.log("networkName: ",networkName)
    //console.log("chain ID: ", chainId)
    const dappTokenAddress = chainId ? networkMapping[String(chainId)]["DappToken"][0]:  constants.AddressZero
    const wethTokenAddress = chainId ? brownieConfig["networks"][networkName]["weth_token"]: constants.AddressZero
    const daiTokenAddress = chainId ? brownieConfig["networks"][networkName]["fau_token"]: constants.AddressZero

    const supportedTokens: Array<Token> = [
        {
            image: dappImg,
            address: dappTokenAddress,
            name: "DAPP"
        },
        {
            image: ethImg,
            address: wethTokenAddress,
            name: "WETH"
        },
        {
            image: daiImg,
            address: daiTokenAddress,
            name: "DAI"
        }
    ]

    return (<>
    <h2 className={classes.title}>Dapp Token App</h2>
    <YourWallet supportedTokens={supportedTokens} />
    </>)
}